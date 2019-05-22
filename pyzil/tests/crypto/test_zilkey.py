# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License

import os
import re
import json
import pytest

from pyzil.common import utils
from pyzil import crypto


def path_join(*path):
    import os
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(cur_dir, *path)


def load_ts_fixtures(file_name):
    with open(file_name) as f:
        content = f.read()

    results = []
    re_list = re.compile(r"\{(?P<entry>.+?)\},", re.DOTALL)
    for match in re_list.finditer(content):
        entry = match.group("entry")
        items = [item.strip() for item in entry.strip().split(",") if item and item.strip()]
        entry_dict = {}
        for item in items:
            key, value = [v.strip() for v in item.strip().split(":", 2) if v and v.strip()]
            entry_dict[key] = value.strip("'").strip('"')

        results.append(entry_dict)

    return results


class TestZilKey:
    def test_zil_mykey(self):
        key = crypto.ZilKey.load_mykey_txt(path_join("mykey.txt"))
        assert key.address == "967e40168af66f441b73c0146e26069bfc3accc7"

        with pytest.raises(AssertionError):
            crypto.ZilKey("02A349FA10F0E6A614A38D6033588A422357F2C60AF2EEBAE15D06498DF8AF0B05",
                          "75889EA1AF5D402B69E61C654C74D8B569E363D2E271E1E6E2B63FDB9B635173")

        new_key = crypto.ZilKey(
            "02A349FA10F0E6A614A38D6033588A422357F2C60AF2EEBAE15D06498DF8AF0B05",
            "75889EA1AF5D402B69E61C654C74D8B569E363D2E271E1E6E2B63FDB9B635174"
        )

        assert key == new_key
        assert key != crypto.ZilKey.generate_new()

        pub_key = "0x03949D29723DA4B2628224D3EC8E74C518ACA98C6630B00527F86B8349E982CB57"
        private_key = "05C3CF3387F31202CD0798B7AA882327A1BD365331F90954A58C18F61BD08FFC"
        wallet_address = "95B27EC211F86748DD985E1424B4058E94AA5814"

        new_key = crypto.ZilKey(public_key=pub_key)
        assert new_key.address == wallet_address.lower()

        new_key = crypto.ZilKey(private_key=private_key)
        assert utils.hex_str_to_int(new_key.keypair_str.public) == utils.hex_str_to_int(pub_key)

        assert new_key.address == wallet_address.lower()

    def test_sign_verify(self):
        key = crypto.ZilKey.generate_new()
        for i in range(10):
            l = 1 + i * 512
            msg = utils.rand_bytes(l) + utils.rand_string(l).encode()
            signature = key.sign(msg)
            assert isinstance(signature, bytes)
            assert key.verify(signature, msg)
            signature_str = key.sign_str(msg)
            assert isinstance(signature_str, str)
            assert key.verify(signature_str, msg)

    def test_load_mykey(self):
        key = crypto.ZilKey.load_mykey_txt(path_join("mykey.txt"))
        assert key.address == "967e40168af66f441b73c0146e26069bfc3accc7"

        key2 = crypto.ZilKey.load_mykey_txt(path_join("mykey2.txt"))
        assert key2.address == "e2406d084955e2d2ba8e8eaf7fe1c6a3e9ab3ea9"

    def test_address(self):
        addresses = load_ts_fixtures(path_join("address.fixtures.ts"))
        for addr in addresses:
            from_file = addr["address"].lower()
            from_private = crypto.ZilKey(private_key=addr["private"]).address
            assert from_private == from_file
            from_public = crypto.ZilKey(public_key=addr["public"]).address
            assert from_public == from_file

    def test_checksum_address(self):
        addresses = load_ts_fixtures(path_join("checksum.fixtures.ts"))
        for addr in addresses:
            original = addr["original"]
            checksum_addr = crypto.zilkey.to_checksum_address(original)
            assert checksum_addr == addr["zil"]
            assert checksum_addr == "0x" + addr["zil_no0x"]
            assert checksum_addr != addr["eth"]

    def test_keypairs(self):
        keypairs = load_ts_fixtures(path_join("keypairs.fixtures.ts"))
        for pair in keypairs:
            key_from_private = crypto.ZilKey(private_key=pair["private"])
            key_from_public = crypto.ZilKey(public_key=pair["public"])

            assert key_from_private.encoded_public_key == key_from_public.encoded_public_key

    def test_keystore(self):
        key_file = path_join("zilliqa_keystore.json")
        key = crypto.ZilKey.load_keystore("zxcvbnm,", key_file)
        checksum_address = crypto.zilkey.to_checksum_address("526a2719b5855ef7d396a62b912a0dfa08e6ae63")
        assert checksum_address == key.checksum_address

        keystore = key.save_keystore("1234", keystore_file=path_join("zilliqa_keystore3.json"))
        assert keystore["address"] == key.address
        key_file2 = path_join("zilliqa_keystore3.json")
        key2 = crypto.ZilKey.load_keystore("1234", key_file2)
        assert key == key2

        with pytest.raises(ValueError):
            crypto.ZilKey.load_keystore("12345", key_file2)

        os.remove(path_join("zilliqa_keystore3.json"))

    def test_bech32_address(self):
        for addr in json.load(open(path_join("bech32.fixtures.json"))):
            print(addr)
            bech32_addr = crypto.zilkey.to_bech32_address(addr["b16"])
            print(bech32_addr)
            assert bech32_addr == addr["b32"]

            bytes_addr = crypto.zilkey.from_bech32_address(addr["b32"])
            print(bytes_addr)
            assert bytes_addr == crypto.zilkey.to_valid_address(addr["b16"])

            assert crypto.zilkey.is_bech32_address(addr["b32"])
            assert not crypto.zilkey.is_bech32_address(addr["b16"])
