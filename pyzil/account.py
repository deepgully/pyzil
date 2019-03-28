# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License
"""
pyzil.account
~~~~~~~~~~~~

Zilliqa Account

:copyright: (c) 2019 by Gully Chen.
:license: MIT License, see LICENSE for more details.
"""

from pyzil.crypto import zilkey


class Account:
    """Zilliqa Account"""
    def __init__(self, address=None, public_key=None, private_key=None):
        if address is None and public_key is None and private_key is None:
            raise ValueError("missing argument")

        self.address = None
        if address is not None:
            if not zilkey.is_valid_address(address):
                raise ValueError("invalid address")
            self.address = zilkey.to_valid_address(address)

        self.zil_key = None
        if public_key or private_key:
            self.zil_key = zilkey.ZilKey(public_key=public_key, private_key=private_key)

            if self.address is not None:
                if self.zil_key.address != self.address:
                    raise ValueError("mismatch address and zilkey")
            self.address = self.zil_key.address

    def __eq__(self, other):
        if self.zil_key is None and other.zil_key is None:
            return self.address == other.address

        if self.zil_key is None or other.zil_key is None:
            return False

        return self.zil_key == other.zil_key

    @property
    def checksum_address(self):
        return zilkey.to_checksum_address(self.address)

    @property
    def public_key(self):
        return self.zil_key and self.zil_key.keypair_str.public

    @property
    def private_key(self):
        return self.zil_key and self.zil_key.keypair_str.private

    @property
    def keypair(self):
        return self.zil_key and self.zil_key.keypair_str

    @classmethod
    def from_zilkey(cls, zil_key):
        return cls(private_key=zil_key.encoded_private_key)

    @classmethod
    def generate(cls):
        zil_key = zilkey.ZilKey.generate_new()
        return cls.from_zilkey(zil_key)

    @classmethod
    def from_mykey_txt(cls, key_file="mykey.txt"):
        zil_key = zilkey.ZilKey.load_mykey_txt(key_file)
        return cls.from_zilkey(zil_key)

    @classmethod
    def from_keystore(cls, password, keystore_file):
        zil_key = zilkey.ZilKey.load_keystore(password, keystore_file)
        return cls.from_zilkey(zil_key)
