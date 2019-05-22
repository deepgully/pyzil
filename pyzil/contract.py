# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License
"""
pyzil.contract
~~~~~~~~~~~~

Zilliqa Smart Contract

:copyright: (c) 2019 by Gully Chen.
:license: MIT License, see LICENSE for more details.
"""

import json
from enum import Enum
from typing import Dict, List, Optional

from pyzil.crypto import zilkey
from pyzil.zilliqa.chain import active_chain


class Contract:
    """Zilliqa Smart Contract"""
    DEPLOY_ADDRESS = "0x0000000000000000000000000000000000000000"

    class Status(Enum):
        Unknown = "Unknown"
        Deployed = "Deployed"
        Failed = "Failed"
        Rejected = "Rejected"

    @classmethod
    def value_dict(cls, vname: str, vtype: str, value: str) -> dict:
        return {"vname": vname, "type": vtype, "value": value}

    def __init__(self, address: Optional[str]=None, code: Optional[str]=None,
                 init: Optional[List[Dict]]=None, state: Optional[List[Dict]]=None,
                 status: Status=Status.Unknown):
        if address is not None:
            address = zilkey.to_valid_address(address)
            assert address, "invalid address"
        self.address = address
        self.code = code
        self.init = init
        self.state = state
        self.status = status
        self._account = None
        self.last_receipt = None

    def __str__(self):
        return "<Contract Address: {} Status: {}>".format(self.address, self.status)

    __repr__ = __str__

    def __eq__(self, other: "Contract"):
        return self.address == other.address

    @property
    def init_str(self) -> str:
        return json.dumps(self.init)

    @property
    def address0x(self) -> str:
        return self.address and "0x{}".format(self.address)

    @property
    def bech32_address(self) -> str:
        """Return str of bech32 address."""
        return zilkey.to_bech32_address(self.address)

    @property
    def account(self):
        if not self._account:
            raise ValueError("you must set account to deploy/call contract")
        return self._account

    @account.setter
    def account(self, account):
        self._account = account

    @classmethod
    def new_from_code(cls, code: str) -> "Contract":
        return cls(code=code)

    @classmethod
    def load_from_address(cls, address: str, load_state=True) -> "Contract":
        address = zilkey.to_valid_address(address)
        if not address:
            raise ValueError("invalid contract address")

        contract = Contract(address=address, status=cls.Status.Deployed)
        if load_state:
            contract.get_state(get_code=True, get_init=True)
        return contract

    @classmethod
    def get_contracts(cls, owner_address: str) -> List["Contract"]:
        owner_address = zilkey.to_valid_address(owner_address)
        if not owner_address:
            raise ValueError("invalid owner address")
        resp = active_chain.api.GetSmartContracts(owner_address)
        return [
            Contract(
                address=contract["address"],
                state=contract["state"],
                status=Contract.Status.Deployed
            )
            for contract in resp
        ]

    def get_state(self, get_code=False, get_init=False) -> List[Dict]:
        assert self.address, "contract has not been deployed"
        if get_code:
            resp = active_chain.api.GetSmartContractCode(self.address)
            if not resp or "code" not in resp:
                raise ValueError("failed to get contract code")
            self.code = resp["code"]
        if get_init:
            self.init = active_chain.api.GetSmartContractInit(self.address)
        self.state = active_chain.api.GetSmartContractState(self.address)
        return self.state

    def deploy(self, init_params: Optional[List[Dict]]=None,
               nonce: Optional[int]=None,
               gas_price: Optional[int]=None, gas_limit=10000, priority=False,
               confirm=True, timeout=300, sleep=10) -> Optional[Dict]:
        assert self.code, "invalid contract code"

        if self.address or self.status == Contract.Status.Deployed:
            raise ValueError("contract had deployed already")

        init_list = [
            Contract.value_dict("_scilla_version", "Uint32", "0"),
            Contract.value_dict("owner", "ByStr20", self.account.address0x),
        ]
        if init_params is not None:
            init_list += init_params
        self.init = init_list

        txn_info = self.account.transfer(
            to_addr=Contract.DEPLOY_ADDRESS,
            zils=0,
            nonce=nonce,
            gas_price=gas_price,
            gas_limit=gas_limit,
            code=self.code,
            data=self.init_str,
            priority=priority
        )
        if not confirm:
            return txn_info

        if not txn_info:
            raise ValueError("failed to create contract")

        address = txn_info["ContractAddress"]
        deploy_txn_id = txn_info["TranID"]

        txn_details = self.account.wait_txn_confirm(deploy_txn_id, timeout=timeout, sleep=sleep)
        if txn_details:
            self.last_receipt = txn_details["receipt"].copy()

            if txn_details["receipt"]["success"]:
                self.address = active_chain.api.GetContractAddressFromTransactionID(deploy_txn_id)
                assert address == self.address, "address mismatch"
                self.status = Contract.Status.Deployed
            else:
                self.status = Contract.Status.Rejected
        else:
            self.status = Contract.Status.Failed

        return txn_details

    def call(self, method: str,
             params: Optional[List[Dict]],
             nonce: Optional[int] = None,
             gas_price: Optional[int] = None, gas_limit=10000, priority=False,
             confirm=True, timeout=300, sleep=10) -> Optional[Dict]:
        if not self.address:
            raise ValueError("invalid contract address")
        if self.status != Contract.Status.Deployed:
            raise ValueError("contract has not been deployed")

        call_data = json.dumps({
            "_tag": method,
            "params": params
        })

        txn_info = self.account.transfer(
            to_addr=self.address,
            zils=0,
            nonce=nonce,
            gas_price=gas_price,
            gas_limit=gas_limit,
            data=call_data,
            priority=priority
        )
        if not confirm:
            return txn_info

        call_txn_id = txn_info["TranID"]

        txn_details = self.account.wait_txn_confirm(call_txn_id, timeout=timeout, sleep=sleep)
        self.last_receipt = txn_details and txn_details["receipt"]
        return txn_details
