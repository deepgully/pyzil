# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License

from pyzil.common import utils
from pyzil import pow


class TestPoW:
    def test_boundary(self):
        for i in range(256):
            assert pow.boundary_to_difficulty(pow.difficulty_to_boundary(i)) == i

        for i in range(256):
            assert pow.boundary_to_difficulty_divided(
                pow.difficulty_to_boundary_divided(i)
            ) == i

        assert pow.difficulty_to_boundary(31) == pow.difficulty_to_boundary_divided(31)
        assert pow.difficulty_to_boundary(32) == pow.difficulty_to_boundary_divided(32)
        assert pow.difficulty_to_boundary(33) < pow.difficulty_to_boundary_divided(33)
        assert pow.difficulty_to_boundary(33) == pow.difficulty_to_boundary_divided(40)
        assert pow.difficulty_to_boundary(50) == pow.difficulty_to_boundary_divided(176)

        assert pow.difficulty_to_boundary_divided(255) < pow.difficulty_to_boundary_divided(254)

        assert pow.difficulty_to_boundary_divided(33, 4, 32) != pow.difficulty_to_boundary_divided(33, 8, 32)

    def test_pow(self):
        block_num = 22
        header = utils.hex_str_to_bytes("372eca2454ead349c3df0ab5d00b0b706b23e49d469387db91811cee0358fc6d")
        excepted_result = utils.hex_str_to_bytes("00000b184f1fdd88bfd94c86c39e65db0c36144d5e43f745f722196e730cb614")
        excepted_mix = b'/t\xcd\xeb\x19\x8a\xf0\xb9\xab\xe6]"\xd3r\xe2/\xb2\xd4t7\x17t\xa9X<\x1c\xc4\'\xa0y9\xf5'

        nonce = 0x495732e0ed7a801c
        boundary20 = pow.difficulty_to_boundary(20)
        boundary21 = pow.difficulty_to_boundary(21)

        calc_mix_digest, calc_result = pow.pow_hash(block_num, header, nonce)

        assert calc_result == excepted_result
        assert calc_mix_digest == excepted_mix

        assert pow.verify_pow_work(block_num, header, excepted_mix, nonce, boundary20)
        assert not pow.verify_pow_work(block_num, header, excepted_mix, nonce, boundary21)

        assert pow.verify_pow_work(0, header, excepted_mix, nonce, boundary20)
        assert pow.verify_pow_work(29999, header, excepted_mix, nonce, boundary20)
        assert not pow.verify_pow_work(30000, header, excepted_mix, nonce, boundary20)
        assert not pow.verify_pow_work(30001, header, excepted_mix, nonce, boundary20)

