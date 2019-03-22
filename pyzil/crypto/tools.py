# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License
"""
pyzil.crypto.tools
~~~~~~~~~~~~

crypto tools

:copyright: (c) 2019 by Gully Chen.
:license: MIT License, see LICENSE for more details.
"""

import hmac
import hashlib
from typing import Union

from Crypto.Cipher import AES

from pyzil.common import utils


def hash256_bytes(*bytes_hex, encoding="utf-8") -> bytes:
    """Return hash256 digest bytes."""
    m = hashlib.sha256()
    for b in bytes_hex:
        if isinstance(b, str):
            b = b.encode(encoding=encoding)
        m.update(b)
    return m.digest()


def hmac_hash256(key: bytes, msg: bytes) -> bytes:
    """Return bytes of hmac using hash256."""
    h = hmac.new(key, msg, digestmod=hashlib.sha256)
    return h.digest()


def compare_digest(a, b) -> bool:
    return hmac.compare_digest(a, b)


def gen_derived_key(password: Union[str, bytes],
                    kdf_method: str, params: dict) -> bytes:
    """Generate derived key bytes using pbkdf2 or scrypt."""
    if isinstance(password, str):
        password = password.encode()
    salt = params["salt"]
    if isinstance(salt, str):
        salt = utils.hex_str_to_bytes(salt)

    dklen = params["dklen"]
    if kdf_method == "pbkdf2":
        count = params["c"]
        return hashlib.pbkdf2_hmac(
            "sha256", password, salt, count, dklen=dklen
        )
    elif kdf_method == "scrypt":
        return hashlib.scrypt(
            password, salt,
            params["n"], params["r"], params["p"],
            dklen=dklen
        )
    else:
        raise NotImplemented("unsupported kdf method")


def aes_ctr_decrypt(key: bytes, initial_value: bytes,
                    ciphertext: bytes, nonce: bytes=b"") -> bytes:
    cipher = AES.new(key, AES.MODE_CTR,
                     nonce=nonce, initial_value=initial_value)
    return cipher.decrypt(ciphertext)


def aes_ctr_encrypt(key: bytes, initial_value: bytes,
                    ciphertext: bytes, nonce: bytes=b"") -> bytes:
    cipher = AES.new(key, AES.MODE_CTR,
                     nonce=nonce, initial_value=initial_value)
    return cipher.encrypt(ciphertext)
