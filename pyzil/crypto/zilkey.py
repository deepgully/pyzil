# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License
"""
pyzil.crypto.zilkey
~~~~~~~~~~~~

Zilliqa Key

:copyright: (c) 2019 by Gully Chen.
:license: MIT License, see LICENSE for more details.
"""

from typing import Union
from collections import namedtuple

from pyzil.common import utils
from pyzil.crypto import tools, schnorr


# zilliqa address takes the last 20 bytes from hash digest of public key
ADDRESS_NUM_BYTES = 20
ADDRESS_STR_LENGTH = ADDRESS_NUM_BYTES * 2


KeyPair = namedtuple("KeyPair", ["public", "private"])


class ZilKey:
    """ ZIlliqa Key """
    def __init__(self, public_key=None, private_key=None):
        assert public_key or private_key, "public or private key is required"
        if isinstance(public_key, str):
            public_key = utils.hex_str_to_bytes(public_key)
        if isinstance(private_key, str):
            private_key = utils.hex_str_to_bytes(private_key)

        self._bytes_public = public_key
        self._bytes_private = private_key

        # the _pub_key is a Point on curve
        self._public_key = None
        # the private_key is big integer less than curve order
        self._private_key = None

        self._generate_keys()

    def _generate_keys(self):
        if self._bytes_private:
            self._private_key = utils.bytes_to_int(self._bytes_private)
            assert self._private_key < schnorr.CURVE.q
        if self._bytes_public:
            self._public_key = schnorr.decode_public(self._bytes_public)

        if self._private_key and self._public_key:
            _pub_key = schnorr.get_public_key(self._private_key)
            assert _pub_key == self._public_key, "public/private key mismatch"

        # generate public key from private key
        if self._private_key and not self._public_key:
            self._public_key = schnorr.get_public_key(self._private_key)

    @property
    def encoded_public_key(self):
        return schnorr.encode_public(self._public_key.x, self._public_key.y)

    @property
    def encoded_private_key(self):
        return self._private_key and utils.int_to_bytes(self._private_key)

    @property
    def keypair_bytes(self) -> KeyPair:
        return KeyPair(self.encoded_public_key, self.encoded_private_key)

    @property
    def keypair_str(self) -> KeyPair:
        str_pub = utils.bytes_to_hex_str(self.encoded_public_key)
        str_private = self._private_key and utils.int_to_hex_str(self._private_key)
        return KeyPair(str_pub, str_private)

    @property
    def address(self) -> str:
        return tools.hash256_str(self.keypair_bytes.public)[-ADDRESS_STR_LENGTH:]

    def __str__(self):
        return str(self.keypair_str)

    def __eq__(self, other):
        return self._public_key == other._public_key and self._private_key == other._private_key

    @classmethod
    def generate_new(cls):
        """generate new zilliqa key"""
        zil_key = cls(private_key=utils.int_to_bytes(schnorr.gen_private_key()))
        return zil_key

    @classmethod
    def load_mykey_txt(cls, key_file="mykey.txt"):
        with open(key_file, "r") as f:
            str_pub, str_private = f.read().split()
            return ZilKey(public_key=str_pub, private_key=str_private)

    def save_mykey_txt(self, key_file="mykey.txt"):
        with open(key_file, "w") as f:
            str_pub, str_private = self.keypair_str
            f.write(str_pub.upper() + " " + str_private.upper())

    # Zilliqa schnorr signature
    def sign(self, message: bytes) -> bytes:
        """Sign bytes message with private key, return bytes"""
        if not self._private_key:
            raise RuntimeError("missing private key")

        message = utils.ensure_bytes(message)

        return schnorr.sign(message, self.keypair_bytes.private)

    def sign_str(self, message: str) -> str:
        """Sign bytes message with private key, return hex string"""
        message = utils.ensure_bytes(message)
        return utils.bytes_to_hex_str(self.sign(message))

    def verify(self, signature: Union[str, bytes], message: Union[str, bytes]) -> bool:
        """Verify signature with public key."""
        if isinstance(signature, str):
            signature = utils.hex_str_to_bytes(signature)

        message = utils.ensure_bytes(message)

        return schnorr.verify(message, signature, self.keypair_bytes.public)
