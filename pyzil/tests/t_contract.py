# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License

import pytest
from pprint import pprint

from pyzil.zilliqa import chain
from pyzil.account import Account
from pyzil.contract import Contract


def path_join(*path):
    import os
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(cur_dir, *path)


class TestContract:
    chain.set_active_chain(chain.IsolatedServer)
    contracts = {
        "hello": "bd1143caf47101fd1172ff48fc98bdbba9b49fc8",
        "test": "c341f2767efc6bbfbeba0c830b8433addd1885f8",
    }

    account = Account.from_keystore("zxcvbnm,", path_join("crypto", "zilliqa_keystore.json"))

    def _test_new_contract(self):
        print("Account balance1", self.account.get_balance())

        code = open(path_join("contracts", "HelloWorld.scilla")).read()

        contract = Contract.new_from_code(code)
        print(contract)

        with pytest.raises(ValueError, match=".+set account.+"):
            contract.deploy()

        contract.account = self.account
        contract.deploy(timeout=300, sleep=10, gas_price=1000000000)
        print(contract)
        print("Account balance2", self.account.get_balance())
        assert contract.status == Contract.Status.Deployed

    def test_from_address_hello(self):
        address = self.contracts["hello"]
        contract = Contract.load_from_address(address, load_state=True)
        print(contract)
        pprint(contract.get_state(get_code=True, get_init=False))
        print(contract.status)
        print(contract.code)
        pprint(contract.init)
        pprint(contract.state)

    def test_from_address_test(self):
        address = self.contracts["test"]
        contract = Contract.load_from_address(address, load_state=True)
        print(contract)
        pprint(contract.get_state(get_code=True, get_init=False))
        print(contract.status)
        print(contract.code)
        pprint(contract.init)
        pprint(contract.state)

    def test_get_contracts(self):
        owner_addr = self.account.address
        contracts = Contract.get_contracts(owner_addr)
        pprint(contracts)

        contracts2 = self.account.get_contracts()
        pprint(contracts2)

        assert contracts == contracts2

    def test_call(self):
        address = self.contracts["test"]
        contract = Contract.load_from_address(address)
        print(contract)
        contract.get_state(get_init=True, get_code=False)
        print(contract.status)
        pprint(contract.init)
        pprint(contract.state)

        contract.account = self.account
        resp = contract.call(gas_price=1000000000, method="getMessage", params=[])
        print(resp)
        pprint(contract.last_receipt)
        assert contract.last_receipt["success"]
        assert contract.last_receipt["event_logs"][0]["params"][0]["vname"] == "msg"
        assert contract.last_receipt["event_logs"][0]["params"][0]["value"] == "Test Message"

    def test_call_hello(self):
        address = self.contracts["hello"]
        contract = Contract.load_from_address(address)
        print(contract)
        print(contract.status)
        pprint(contract.state)

        contract.account = self.account
        resp = contract.call(gas_price=1000000000, method="contrAddr", params=[])
        print(resp)
        pprint(contract.last_receipt)
        assert contract.last_receipt["success"]
        assert contract.last_receipt["event_logs"][0]["params"][0]["vname"] == "addr"
        assert contract.last_receipt["event_logs"][0]["params"][0]["value"] == contract.address0x

        resp = contract.call(gas_price=1000000000, method="setHello", params=[Contract.value_dict("msg", "String", "hi contract.")])
        print(resp)
        pprint(contract.last_receipt)
        assert contract.last_receipt["success"]
        assert contract.last_receipt["event_logs"][0]["params"][0]["vname"] == "code"
        assert contract.last_receipt["event_logs"][0]["params"][0]["type"] == "Int32"
        assert contract.last_receipt["event_logs"][0]["params"][0]["value"] == "2"

        resp = contract.call(gas_price=1000000000, method="getHello", params=[])
        print(resp)
        pprint(contract.last_receipt)
        assert contract.last_receipt["success"]
        assert contract.last_receipt["event_logs"][0]["_eventname"] == "getHello()"
        assert contract.last_receipt["event_logs"][0]["params"][0]["vname"] == "msg"
        assert contract.last_receipt["event_logs"][0]["params"][0]["type"] == "String"
        assert contract.last_receipt["event_logs"][0]["params"][0]["value"] == "hi contract."

    def test_call_other_account(self):
        address = self.contracts["hello"]
        contract = Contract.load_from_address(address)
        print(contract)
        print(contract.status)

        account2 = Account(private_key="d0b47febbef2bd0c4a4ee04aa20b60d61eb02635e8df5e7fd62409a2b1f5ddf8")
        print("Account2 balance", account2.get_balance())

        contract.account = account2
        resp = contract.call(gas_price=1000000000, method="setHello", params=[
            Contract.value_dict("msg", "String", "hello from another account")
        ])
        print(resp)
        pprint(contract.last_receipt)
        assert contract.last_receipt["success"]
        assert contract.last_receipt["event_logs"][0]["params"][0]["vname"] == "code"
        assert contract.last_receipt["event_logs"][0]["params"][0]["value"] == "1"

        resp = contract.call(gas_price=1000000000, method="getHello", params=[])
        print(resp)
        pprint(contract.last_receipt)
        assert contract.last_receipt["success"]
        assert contract.last_receipt["event_logs"][0]["_eventname"] == "getHello()"
        assert contract.last_receipt["event_logs"][0]["params"][0]["vname"] == "msg"
        assert contract.last_receipt["event_logs"][0]["params"][0]["type"] == "String"
        assert contract.last_receipt["event_logs"][0]["params"][0]["value"] == "hi contract."


