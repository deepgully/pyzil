# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License
"""
pyzil.pow
~~~~~~~~~~~~

This module implements Zilliqa PoW methods

:copyright: (c) 2019 by Gully Chen.
:license: MIT License, see LICENSE for more details.
"""


from typing import List, Tuple, Optional, Union
from collections import OrderedDict

from pyzil.common import utils

from pyethash import (
    EPOCH_LENGTH,
    hashimoto_light,
    get_seedhash,
    mkcache_bytes,
)
from eth_hash.auto import keccak


MAX_EPOCH = 2048


def block_num_to_seed(block_number: int) -> bytes:
    """DS block number to seed hash."""
    return get_seedhash(block_number)


def seed_to_epoch_num(seed: bytes) -> int:
    """Seed to epoch number."""
    for epoch in range(MAX_EPOCH):
        block_num = epoch * EPOCH_LENGTH + 1
        calc_seed = block_num_to_seed(block_num)
        if seed == calc_seed:
            return epoch
    raise ValueError("epoch number out of range, max 2048")


def seed_to_block_num(seed: bytes) -> int:
    """Seed to DS block number."""
    return seed_to_epoch_num(seed) * EPOCH_LENGTH


ZERO_MASK = [0xFF, 0x7F, 0x3F, 0x1F, 0x0F, 0x07, 0x03, 0x01]


def difficulty_to_boundary(difficulty: int) -> bytes:
    """Zilliqa difficulty level to boundary."""
    boundary = bytearray(b"\xFF" * 32)
    n_bytes_to_zero = difficulty // 8
    n_bits_to_zero = difficulty % 8

    boundary[0:n_bytes_to_zero] = b"\x00" * n_bytes_to_zero
    boundary[n_bytes_to_zero] = ZERO_MASK[n_bits_to_zero]

    return bytes(boundary)


def boundary_to_difficulty(boundary) -> int:
    """Boundary to Zilliqa difficulty level."""
    if isinstance(boundary, str):
        boundary = utils.hex_str_to_bytes(boundary)

    difficulty = 0
    for b in memoryview(boundary):
        if b == 0x00:
            difficulty += 8
        else:
            difficulty += (8 - b.bit_length())
            break
    return difficulty


assert boundary_to_difficulty(difficulty_to_boundary(11)) == 11


def difficulty_to_boundary_divided(difficulty: int, n_divided: int=8,
                                   n_divided_start: int=32) -> bytes:
    """Zilliqa divided difficulty to boundary."""
    if difficulty < n_divided_start:
        return difficulty_to_boundary(difficulty)

    n_level = (difficulty - n_divided_start) // n_divided
    m_sub_level = (difficulty - n_divided_start) % n_divided
    difficulty_level = n_divided_start + n_level

    int_boundary = utils.bytes_to_int(difficulty_to_boundary(difficulty_level))
    boundary_change_step = (int_boundary >> 1) // n_divided

    int_boundary -= boundary_change_step * m_sub_level

    return utils.int_to_bytes(int_boundary, n_bytes=32)


def boundary_to_difficulty_divided(boundary, n_divided: int=8,
                                   n_divided_start: int=32) -> int:
    """Boundary to divided difficulty."""
    if isinstance(boundary, str):
        boundary = utils.hex_str_to_bytes(boundary)

    difficulty_level = boundary_to_difficulty(boundary)
    if difficulty_level < n_divided_start:
        return difficulty_level

    n_level = difficulty_level - n_divided_start

    int_cur_boundary = utils.bytes_to_int(boundary)
    int_cur_level = utils.bytes_to_int(difficulty_to_boundary(difficulty_level))

    step = (int_cur_level >> 1) // n_divided
    m_sub_level = (int_cur_level - int_cur_boundary) // step

    new_difficulty = n_divided_start + n_level * n_divided + m_sub_level
    return new_difficulty


assert boundary_to_difficulty_divided(difficulty_to_boundary_divided(31)) == 31
assert boundary_to_difficulty_divided(difficulty_to_boundary_divided(32)) == 32
assert boundary_to_difficulty_divided(difficulty_to_boundary_divided(49)) == 49
assert boundary_to_difficulty_divided(difficulty_to_boundary_divided(255)) == 255
assert boundary_to_difficulty_divided(difficulty_to_boundary(31)) == 31


def boundary_to_hashpower(boundary: Union[str, bytes]) -> int:
    """boundary to hashrate."""
    dividend = 0xffff000000000000000000000000000000000000000000000000000000000000
    if isinstance(boundary, str):
        return dividend // utils.hex_str_to_int(boundary)
    elif isinstance(boundary, bytes):
        return dividend // utils.bytes_to_int(boundary)
    raise TypeError("Type of boundary should be str or bytes")


def difficulty_to_hashpower(difficulty: int) -> int:
    """difficulty level to hashrate."""
    return boundary_to_hashpower(difficulty_to_boundary(difficulty))


def difficulty_to_hashpower_divided(difficulty: int, n_divided: int=8,
                                    n_divided_start: int=32) -> int:
    """divided difficulty to hashrate."""
    return boundary_to_hashpower(
        difficulty_to_boundary_divided(
            difficulty, n_divided=n_divided, n_divided_start=n_divided_start
        )
    )


def is_less_or_equal(hash_1: Union[str, bytes],
                     hash_2: Union[str, bytes]) -> bool:
    """check hash result."""
    if isinstance(hash_1, str):
        hash_1 = utils.hex_str_to_bytes(hash_1)
    if isinstance(hash_2, str):
        hash_2 = utils.hex_str_to_bytes(hash_2)
    assert isinstance(hash_1, bytes)
    assert isinstance(hash_2, bytes)

    return utils.bytes_to_int(hash_1) <= utils.bytes_to_int(hash_2)


# for pow verify
def verify_pow_work(block_number: int, header: bytes, mix_digest: bytes,
                    nonce: int, boundary: bytes) -> Optional[bytes]:
    """Return hash rate if it less than boundary."""
    calc_mix_digest, calc_result = pow_hash(block_number, header, nonce)

    if mix_digest != calc_mix_digest:
        return None

    ok = is_less_or_equal(calc_result, boundary)
    if not ok:
        return None
    return calc_result


# ethash settings
CACHE_MAX_ITEMS = 10
cache_seeds = bytearray(b"\x00" * 32)     # type: List[bytes]
cache_by_seed = OrderedDict()             # type: OrderedDict[bytes, bytearray]


def get_cache(block_number: int) -> bytes:
    """helper function for ethash."""
    while len(cache_seeds) <= block_number // EPOCH_LENGTH:
        cache_seeds.append(keccak(cache_seeds[-1]))
    seed = cache_seeds[block_number // EPOCH_LENGTH]
    if seed in cache_by_seed:
        c = cache_by_seed.pop(seed)  # pop and append at end
        cache_by_seed[seed] = c
        return c
    c = mkcache_bytes(block_number)
    cache_by_seed[seed] = c
    if len(cache_by_seed) > CACHE_MAX_ITEMS:
        cache_by_seed.popitem(last=False)  # remove last recently accessed
    return c


def pow_hash(block_number, header, nonce) -> Tuple[bytes, bytes]:
    """search for hash result using hashimoto_light."""
    cache_bytes = get_cache(block_number)
    hash_ret = hashimoto_light(block_number, cache_bytes, header, nonce)
    return hash_ret[b"mix digest"], hash_ret[b"result"]
