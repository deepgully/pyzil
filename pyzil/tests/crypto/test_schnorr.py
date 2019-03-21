# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License

import os
import json
import random

from pyzil.common import utils
from pyzil.crypto import ZilKey
from pyzil.crypto import schnorr

h2b = utils.hex_str_to_bytes
b2i = utils.bytes_to_int
cur_dir = os.path.dirname(os.path.abspath(__file__))


class TestSchnorr:
    def test_vectors(self):
        vectors = json.load(open(os.path.join(cur_dir, "schnorr.fixtures.json")))
        for vector in random.choices(vectors, k=100):
            for key in vector:
                if isinstance(vector[key], bytes):
                    continue
                vector[key] = h2b(vector[key])

            sign = schnorr.sign_with_k(
                vector["msg"],
                vector["priv"],
                b2i(vector["k"])
            )
            assert not not sign

            r, s = schnorr.decode_signature(sign)
            assert r == b2i(vector["r"])
            assert s == b2i(vector["s"])

            sign = schnorr.encode_signature(r, s)

            assert schnorr.verify(vector["msg"], sign, vector["pub"])

    def test_sign_verify(self):
        for i in range(10):
            msg = utils.rand_bytes(1 + i * 512)
            key = ZilKey.generate_new()

            signature1 = schnorr.sign(msg, key.keypair_bytes.private)
            signature2 = schnorr.sign(msg, key.keypair_bytes.private)

            assert signature1 != signature2
            assert schnorr.verify(msg, signature1, key.keypair_bytes.public)
            assert schnorr.verify(msg, signature2, key.keypair_bytes.public)

    def test_encode_decode(self):
        for i in range(10):
            priv_key = schnorr.gen_private_key()
            pub_key = schnorr.get_public_key(priv_key)

            encoded_pub = schnorr.encode_public(pub_key.x, pub_key.y,
                                                compressed=True)
            decoded_pub = schnorr.decode_public(encoded_pub)

            assert pub_key == decoded_pub

            encoded_pub = schnorr.encode_public(pub_key.x, pub_key.y,
                                                compressed=False)
            decoded_pub = schnorr.decode_public(encoded_pub)

            assert pub_key == decoded_pub
