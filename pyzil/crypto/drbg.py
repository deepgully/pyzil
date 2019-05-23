# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License
"""
pyzil.crypto.drbg
~~~~~~~~~~~~

HMAC DRBG implementation of Nist SP 800-90A

:copyright: (c) 2019 by Gully Chen.
:license: MIT License, see LICENSE for more details.
"""

import hmac
import logging
import secrets
import hashlib


ENTROPY_BYTES = 32


def randbelow_drbg(boundary, nonce=None):
    """Return a random int in the range (0, n)."""
    if boundary <= 0:
        raise ValueError("boundary cannot be less than zero")
    num_bytes = (boundary.bit_length() + 7) // 8

    if nonce is None:
        nonce = secrets.token_bytes(ENTROPY_BYTES)

    entropy = nonce + secrets.token_bytes(ENTROPY_BYTES)

    drbg = HMAC_DRBG(entropy, personalization_string=b"pyzil_hmac_drbg")
    while True:
        rand_bytes = drbg.generate(num_bytes)
        if rand_bytes is None:
            logging.critical("reseed HMAC DRBG")
            drbg.reseed(nonce + secrets.token_bytes(ENTROPY_BYTES))
            continue

        r = int.from_bytes(rand_bytes, byteorder="big")
        if r < boundary:
            break
    return r


class HMAC_DRBG(object):
    """
    A Python implementation of HMAC_DRBG, as specified by NIST SP 800-90A.
    https://github.com/fpgaminer/python-hmac-drbg/blob/master/hmac_drbg/hmac_drbg.py
    """
    def __init__(self, entropy, requested_security_strength=256, personalization_string=b""):
        if requested_security_strength > 256:
            raise RuntimeError("requested_security_strength cannot exceed 256 bits.")

        # Modified from Appendix D, which specified 160 bits here
        if len(personalization_string) * 8 > 256:
            raise RuntimeError("personalization_string cannot exceed 256 bits.")

        if requested_security_strength <= 112:
            self.security_strength = 112
        elif requested_security_strength <= 128:
            self.security_strength = 128
        elif requested_security_strength <= 192:
            self.security_strength = 192
        else:
            self.security_strength = 256

        if (len(entropy) * 8 * 2) < (3 * self.security_strength):
            raise RuntimeError("entropy must be at least %f bits." % (1.5 * self.security_strength))

        self.K = None
        self.V = None
        self.reseed_counter = 1
        self._instantiate(entropy, personalization_string)

    def _hmac(self, key, data):
        return hmac.new(key, data, hashlib.sha256).digest()

    def _update(self, provided_data=None):
        self.K = self._hmac(self.K, self.V + b"\x00" + (b"" if provided_data is None else provided_data))
        self.V = self._hmac(self.K, self.V)

        if provided_data is not None:
            self.K = self._hmac(self.K, self.V + b"\x01" + provided_data)
            self.V = self._hmac(self.K, self.V)

    def _instantiate(self, entropy, personalization_string):
        seed_material = entropy + personalization_string

        self.K = b"\x00" * 32
        self.V = b"\x01" * 32

        self._update(seed_material)
        self.reseed_counter = 1

    def reseed(self, entropy):
        if (len(entropy) * 8) < self.security_strength:
            raise RuntimeError("entropy must be at least %f bits." % self.security_strength)

        self._update(entropy)
        self.reseed_counter = 1

    def generate(self, num_bytes, requested_security_strength=256):
        if (num_bytes * 8) > 7500:
            raise RuntimeError("generate cannot generate more than 7500 bits in a single call.")

        if requested_security_strength > self.security_strength:
            raise RuntimeError(
                "requested_security_strength exceeds this instance's security_strength (%d)" % self.security_strength)

        if self.reseed_counter >= 10000:
            return None

        temp = b""

        while len(temp) < num_bytes:
            self.V = self._hmac(self.K, self.V)
            temp += self.V

        self._update(None)
        self.reseed_counter += 1

        return temp[:num_bytes]
