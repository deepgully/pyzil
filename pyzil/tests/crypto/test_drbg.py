# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License

import os

from pyzil.common import utils
from pyzil.crypto import drbg

h2b = utils.hex_str_to_bytes
b2i = utils.bytes_to_int
cur_dir = os.path.dirname(os.path.abspath(__file__))


ENTRY_NAMES = [
    "EntropyInput", "Nonce", "PersonalizationString", "EntropyInputReseed",
    "AdditionalInputReseed", "AdditionalInput", "AdditionalInput", "ReturnedBits"
]


def read_entry(f, expected_name):
    name, value = f.readline().strip().split("=")
    name, value = name.strip(), value.strip()
    assert name == expected_name
    if not value:
        return b""
    return utils.hex_str_to_bytes(value)


def load_vectors():
    vectors = []
    with open(os.path.join(cur_dir, "hmac_drbg.rsp"), "r") as f:
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip()
            if not line or line.startswith("["):
                continue
            if line.startswith("COUNT"):
                vector = {}
                for name in ENTRY_NAMES:
                    vector[name] = read_entry(f, name)
                vectors.append(vector)
    return vectors


class TestDRBG:
    def test_vectors(self):
        for vector in load_vectors():
            hmac_drbg = drbg.HMAC_DRBG(
                entropy=(vector["EntropyInput"] + vector["Nonce"]),
                personalization_string=vector["PersonalizationString"]
            )
            hmac_drbg.reseed(entropy=vector["EntropyInputReseed"])
            bits_len = len(vector["ReturnedBits"])
            hmac_drbg.generate(bits_len)
            result = hmac_drbg.generate(bits_len)

            assert result == vector["ReturnedBits"]
