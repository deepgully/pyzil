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

import json
import uuid
from typing import Union, Optional
from collections import namedtuple

from pyzil.common import utils
from pyzil.crypto import tools, schnorr, bech32


# zilliqa address takes the last 20 bytes from hash digest of public key
ADDRESS_NUM_BYTES = 20
ADDRESS_STR_LENGTH = ADDRESS_NUM_BYTES * 2


def is_valid_address(address: str) -> bool:
    """Return True if address is valid."""
    if address.lower().startswith("0x"):
        address = address[2:]
    if len(address) != ADDRESS_STR_LENGTH:
        return False
    # noinspection PyBroadException
    try:
        utils.hex_str_to_int(address)
    except Exception:
        return False
    return True


def to_valid_address(address: str) -> Optional[str]:
    """Return lower case address if address is valid."""
    if is_bech32_address(address):
        address = from_bech32_address(address)

    if not is_valid_address(address):
        return None
    address = address.lower()
    if address.startswith("0x"):
        address = address[2:]
    return address


def to_checksum_address(address: str, prefix="0x") -> Optional[str]:
    """Convert address to checksum address."""
    if is_bech32_address(address):
        address = from_bech32_address(address)

    if not is_valid_address(address):
        return None

    address = address.lower().replace("0x", "")
    address_bytes = utils.hex_str_to_bytes(address)
    v = utils.bytes_to_int(tools.hash256_bytes(address_bytes))

    checksum_address = prefix
    for i, c in enumerate(address):
        if not c.isdigit():
            if v & (1 << 255 - 6 * i):
                c = c.upper()
            else:
                c = c.lower()
        checksum_address += c

    return checksum_address


def is_valid_checksum_address(address: str) -> bool:
    """Return True if address is valid checksum address."""
    if not is_valid_address(address):
        return False
    return to_checksum_address(address) == address


def to_bech32_address(address: str) -> Optional[str]:
    """Convert 20 bytes address to bech32 address."""
    if not is_valid_address(address):
        return None
    return bech32.encode("zil", utils.hex_str_to_bytes(address))


def from_bech32_address(bech32_address: str) -> Optional[str]:
    """Convert bech32 address to 20 bytes address."""
    data = bech32.decode("zil", bech32_address)
    if data is None:
        return None
    address = utils.bytes_to_hex_str(bytes(data))
    return to_valid_address(address)


def is_bech32_address(bech32_address: str) -> bool:
    """Return True if address is valid bech32 address."""
    if not bech32_address.startswith("zil1"):
        return False
    return from_bech32_address(bech32_address) is not None


KeyPair = namedtuple("KeyPair", ["public", "private"])


class ZilKey:
    """ Zilliqa Key """
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
        """bytes of public key."""
        return schnorr.encode_public(self._public_key.x, self._public_key.y)

    @property
    def encoded_private_key(self):
        """bytes of private key."""
        return self._private_key and utils.int_to_bytes(self._private_key)

    @property
    def keypair_bytes(self) -> KeyPair:
        """bytes of key pair."""
        return KeyPair(self.encoded_public_key, self.encoded_private_key)

    @property
    def keypair_str(self) -> KeyPair:
        """hex string of key pair."""
        str_pub = utils.bytes_to_hex_str(self.encoded_public_key)
        str_private = self._private_key and utils.int_to_hex_str(self._private_key)
        return KeyPair(str_pub, str_private)

    @property
    def address(self) -> str:
        addr_bytes = tools.hash256_bytes(self.keypair_bytes.public)
        return utils.bytes_to_hex_str(addr_bytes)[-ADDRESS_STR_LENGTH:]

    @property
    def checksum_address(self) -> str:
        return to_checksum_address(self.address)

    def __str__(self):
        return str(self.keypair_str)

    def __eq__(self, other):
        return self._public_key == other._public_key and self._private_key == other._private_key

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

    @classmethod
    def generate_new(cls):
        """Generate new zilliqa key"""
        zil_key = cls(private_key=utils.int_to_bytes(schnorr.gen_private_key()))
        return zil_key

    @classmethod
    def load_mykey_txt(cls, key_file="mykey.txt"):
        """Load Zilliqa key from mykey.txt."""
        with open(key_file, "r") as f:
            str_pub, str_private = f.read().split()
            return ZilKey(public_key=str_pub, private_key=str_private)

    def save_mykey_txt(self, key_file="mykey.txt"):
        """Save key to mykey.txt."""
        with open(key_file, "w") as f:
            str_pub, str_private = self.keypair_str
            f.write(str_pub.upper() + " " + str_private.upper())

    @classmethod
    def load_keystore(cls, password: str, keystore_file):
        """Load Zilliqa key from keystore json file."""
        if hasattr(keystore_file, "read"):
            keystore = json.load(keystore_file)
        else:
            with open(keystore_file) as f:
                keystore = json.load(f)

        checksum_address = to_checksum_address(keystore["address"])
        ciphertext = utils.hex_str_to_bytes(keystore["crypto"]["ciphertext"])
        iv = utils.hex_str_to_bytes(keystore["crypto"]["cipherparams"]["iv"])

        kdf_method = keystore["crypto"]["kdf"]
        kdfparams = keystore["crypto"]["kdfparams"]

        derived_key = tools.gen_derived_key(password, kdf_method, kdfparams)

        cipher = keystore["crypto"]["cipher"].encode()
        message = derived_key[16:32] + ciphertext + iv + cipher
        mac_generated = tools.hmac_hash256(derived_key, msg=message)

        mac_from_file = utils.hex_str_to_bytes(keystore["crypto"]["mac"])
        if not tools.compare_digest(mac_generated, mac_from_file):
            raise ValueError("Invalid password or keystore file")

        key = derived_key[:16]
        private_key = tools.aes_ctr_decrypt(key, iv, ciphertext)
        zilkey = cls(private_key=private_key)
        if not tools.compare_digest(checksum_address, zilkey.checksum_address):
            raise ValueError("Invalid keystore file, address mismatch")
        return zilkey

    def save_keystore(self, password: str, kdf_method: str="pbkdf2",
                      keystore_file=None) -> dict:
        """Save Zilliqa key to keystore, format details on
        https://github.com/ethereum/wiki/wiki/Web3-Secret-Storage-Definition.
        """
        address = self.address
        cipher = "aes-128-ctr"
        salt = utils.rand_bytes(32)
        iv = utils.rand_bytes(16)
        kdfparams = {
            "salt": utils.bytes_to_hex_str(salt),
            "n": 8192,
            "c": 262144,
            "r": 8,
            "p": 1,
            "dklen": 32
        }
        derived_key = tools.gen_derived_key(password, kdf_method, kdfparams)

        key = derived_key[:16]
        ciphertext = tools.aes_ctr_encrypt(key, iv,
                                           ciphertext=self.encoded_private_key)
        cipher_bytes = cipher.encode()
        message = derived_key[16:32] + ciphertext + iv + cipher_bytes
        mac_generated = tools.hmac_hash256(derived_key, msg=message)

        keystore = {
            "address": address,
            "crypto": {
                "cipher": cipher,
                "cipherparams": {
                    "iv": utils.bytes_to_hex_str(iv),
                },
                "ciphertext": utils.bytes_to_hex_str(ciphertext),
                "kdf": kdf_method,
                "kdfparams": kdfparams,
                "mac": utils.bytes_to_hex_str(mac_generated),
            },
            "id": str(uuid.uuid4()),
            "version": 3,
        }

        if keystore_file is None:
            return keystore
        if hasattr(keystore_file, "write"):
            json.dump(keystore, keystore_file)
        else:
            with open(keystore_file, "w") as f:
                json.dump(keystore, f)
        return keystore
