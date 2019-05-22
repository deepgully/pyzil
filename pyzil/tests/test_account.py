# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License

import pytest
from pprint import pprint

from pyzil.crypto import zilkey
from pyzil.zilliqa import chain
from pyzil.account import Account, BatchTransfer
from pyzil.zilliqa.units import Zil, Qa


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

        addr = "1d19918a737306218b5cbb3241fcdcbd998c3a72"
        bech32_addr = "zil1r5verznnwvrzrz6uhveyrlxuhkvccwnju4aehf"
        account1 = Account(address=addr)
        account2 = Account(address=bech32_addr)
        assert account1 == account2
        assert account1.bech32_address == bech32_addr
        assert account2.address == addr

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

        account3 = Account.from_keystore("zxcvbnm,", path_join("crypto", "zilliqa_keystore.json"))
        balance = account3.get_balance()
        print("balance", balance)
        assert balance > 0

    def _test_transfer(self):
        chain.set_active_chain(chain.TestNet)

        account = Account(address="b50c2404e699fd985f71b2c3f032059f13d6543b")
        print(account)
        balance1 = account.get_balance()
        print("Account1 balance", balance1)
        with pytest.raises(RuntimeError):
            account.transfer("to_addr", 1)

        account2 = Account.from_keystore("zxcvbnm,", path_join("crypto", "zilliqa_keystore.json"))
        print(account2)
        balance = account2.get_balance()
        print("Account2 balance", balance)
        assert balance > 0

        to_addr = account.address
        with pytest.raises(ValueError):
            account2.transfer(to_addr, 50000)

        txn_info = account2.transfer(to_addr, Zil(10.3))
        pprint(txn_info)

        txn_details = account2.wait_txn_confirm(txn_info["TranID"], timeout=120)
        pprint(txn_details)
        assert txn_details

        balance2 = account.get_balance()
        print("Account1 balance", balance2)
        assert balance2 >= balance1 + 10.3

        account = Account(private_key="d0b47febbef2bd0c4a4ee04aa20b60d61eb02635e8df5e7fd62409a2b1f5ddf8")
        txn_info = account.transfer(account2.address, 10.3)
        pprint(txn_info)

    def _test_batch_transfer(self):
        chain.set_active_chain(chain.TestNet)

        account = Account.from_keystore("zxcvbnm,", path_join("crypto", "zilliqa_keystore.json"))
        print(account)
        balance = account.get_balance()
        print("Account balance", balance)
        assert balance > 0

        with pytest.raises(ValueError):
            account.transfer_batch([
                BatchTransfer("b50c2404e699fd985f71b2c3f032059f13d6543b", 0),
                BatchTransfer("wrong_address", 0)
            ])

        batch = []
        total_zils = 0
        for i in range(10):
            batch.append(BatchTransfer(
                "b50c2404e699fd985f71b2c3f032059f13d6543b",
                Zil(i * 0.1))
            )
            total_zils += (i * 0.1)

        pprint(batch)
        batch.append(BatchTransfer("b50c2404e699fd985f71b2c3f032059f13d6543b", 500000))
        batch.append(BatchTransfer("b50c2404e699fd985f71b2c3f032059f13d6543b", 0))

        txn_infos = account.transfer_batch(batch)
        pprint(txn_infos)

        txn_details = account.wait_txn_confirm(txn_infos[0]["TranID"], timeout=120)
        pprint(txn_details)
        assert txn_details

        for txn_info in txn_infos:
            if not txn_info:
                print("Failed to create txn")
            else:
                txn_details = account.wait_txn_confirm(txn_info["TranID"])
                pprint(txn_details)
                if txn_details and txn_details["receipt"]["success"]:
                    print("Txn success")
                else:
                    print("Txn failed")

        balance2 = account.get_balance()
        print("Account1 balance", balance2)

        account2 = Account(private_key="d0b47febbef2bd0c4a4ee04aa20b60d61eb02635e8df5e7fd62409a2b1f5ddf8")
        txn_info = account2.transfer(account.address, total_zils)
        pprint(txn_info)

    def _test_transfer_qa(self):
        chain.set_active_chain(chain.TestNet)

        account = Account(address="b50c2404e699fd985f71b2c3f032059f13d6543b")
        print(account)
        print("Account1 balance", repr(account.get_balance()))

        account2 = Account.from_keystore("zxcvbnm,", path_join("crypto", "zilliqa_keystore.json"))
        print(account2)
        balance = account2.get_balance()
        print("Account2 balance", repr(balance))
        assert balance > 0

        to_addr = account.address
        txn_info = account2.transfer(to_addr, Qa(123456789))
        pprint(txn_info)

        txn_details = account2.wait_txn_confirm(txn_info["TranID"], timeout=120)
        pprint(txn_details)
        assert txn_details

        print("Account1 balance", repr(account.get_balance()))
        print("Account1 balance", repr(account.get_balance_qa()))

        account = Account(private_key="d0b47febbef2bd0c4a4ee04aa20b60d61eb02635e8df5e7fd62409a2b1f5ddf8")
        txn_info = account.transfer(account2.checksum_address, Qa(123456789))
        pprint(txn_info)

    def test_transfer_confirm(self):
        chain.set_active_chain(chain.TestNet)

        account = Account(address="b50c2404e699fd985f71b2c3f032059f13d6543b")
        print(account)
        balance1 = account.get_balance()
        print("Account1 balance", balance1)
        with pytest.raises(RuntimeError):
            account.transfer("to_addr", 1)

        account2 = Account.from_keystore("zxcvbnm,", path_join("crypto", "zilliqa_keystore.json"))
        print(account2)
        balance = account2.get_balance()
        print("Account2 balance", balance)
        assert balance > 0

        to_addr = account.address
        result = account2.transfer(to_addr, Zil(10.3), confirm=True, timeout=300, sleep=20)
        print("Transfer Result", result)
        pprint(account2.last_params)
        pprint(account2.last_txn_info)
        pprint(account2.last_txn_details)

        balance2 = account.get_balance()
        print("Account1 balance", balance2)
        assert balance2 >= balance1 + 10.3

        account = Account(private_key="d0b47febbef2bd0c4a4ee04aa20b60d61eb02635e8df5e7fd62409a2b1f5ddf8")
        result = account.transfer(account2.address, 10.3, confirm=True, timeout=600, sleep=20)
        print("Transfer Result", result)
        pprint(account2.last_params)
        pprint(account2.last_txn_info)
        pprint(account2.last_txn_details)
