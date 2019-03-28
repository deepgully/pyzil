# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License

import pytest

from pyzil.crypto import zilkey
from pyzil.zilliqa import chain
from pyzil.account import Account


def path_join(*path):
    import os
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(cur_dir, *path)


class TestAccount:
    def test_new_account(self):
        with pytest.raises(ValueError):
            Account()

        account = Account.generate()
        assert account and account.address
        assert account.zil_key.address == account.address

        address = "b50c2404e699fd985f71b2c3f032059f13d6543b"
        account = Account(address=address)
        assert account and account.address
        assert account.checksum_address == zilkey.to_checksum_address(address)
        assert account.zil_key is None

        pub_key = "0x03949D29723DA4B2628224D3EC8E74C518ACA98C6630B00527F86B8349E982CB57"
        private_key = "05C3CF3387F31202CD0798B7AA882327A1BD365331F90954A58C18F61BD08FFC"
        address = "95B27EC211F86748DD985E1424B4058E94AA5814"

        account = Account(address=address, private_key=private_key)
        assert account and account.address
        assert account.checksum_address == zilkey.to_checksum_address(address)
        assert account.zil_key is not None

        account = Account(address=address, public_key=pub_key)
        assert account and account.address
        assert account.checksum_address == zilkey.to_checksum_address(address)
        assert account.zil_key is not None

        account = Account(address=address, public_key=pub_key, private_key=private_key)
        assert account and account.address
        assert account.checksum_address == zilkey.to_checksum_address(address)
        assert account.zil_key is not None

    def test_load_mykey_txt(self):
        account = Account.from_mykey_txt(path_join("crypto", "mykey.txt"))
        assert account and account.address == "967e40168af66f441b73c0146e26069bfc3accc7"

        account = Account.from_mykey_txt(path_join("crypto", "mykey2.txt"))
        assert account and account.address == "e2406d084955e2d2ba8e8eaf7fe1c6a3e9ab3ea9"

    def test_keystore(self):
        account = Account.from_keystore("zxcvbnm,", path_join("crypto", "zilliqa_keystore.json"))
        assert account and account.address == "526a2719b5855ef7d396a62b912a0dfa08e6ae63"

        account = Account.from_keystore("1234", path_join("crypto", "zilliqa_keystore2.json"))
        assert account and account.address == "526a2719b5855ef7d396a62b912a0dfa08e6ae63"

        with pytest.raises(ValueError):
            account = Account.from_keystore("123", path_join("crypto", "zilliqa_keystore2.json"))
            assert account and account.address == "526a2719b5855ef7d396a62b912a0dfa08e6ae63"

    def test_balance(self):
        account = Account(address="b50c2404e699fd985f71b2c3f032059f13d6543b")
        print("set active chain to TestNet")
        chain.set_active_chain(chain.TestNet)
        balance = account.get_balance()
        print("balance", balance)
        assert balance > 0

        nonce = account.get_nonce()
        print("nonce", nonce)
        assert nonce >= 3

        account2 = Account(address="b50c2404e699fd985f71b2c3f032059f13d65432")
        balance = account2.get_balance()
        print("balance", balance)
        assert balance == 0
