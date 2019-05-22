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

from typing import List, Union, Optional
from collections import namedtuple
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor

from pyzil.crypto import zilkey
from pyzil.zilliqa.api import APIError
from pyzil.zilliqa.chain import active_chain
from pyzil.zilliqa.units import Qa, Zil


BatchTransfer = namedtuple("BatchTransfer", ["to_addr", "zils"])


class Account:
    """Zilliqa Account"""

    _min_gas = None

    def __init__(self, address=None, public_key=None, private_key=None):
        if address is None and public_key is None and private_key is None:
            raise ValueError("missing argument")

        self.address = None
        if address is not None:
            address = zilkey.to_valid_address(address)
            assert address, "invalid address"
            self.address = address

        self.zil_key = None
        if public_key or private_key:
            self.zil_key = zilkey.ZilKey(public_key=public_key, private_key=private_key)

            if self.address is not None:
                if self.zil_key.address != self.address:
                    raise ValueError("mismatch address and zilkey")
            self.address = self.zil_key.address

        self.last_params = None
        self.last_txn_info = None
        self.last_txn_details = None

    def __str__(self):
        return "<Account: {}>".format(self.address)

    def __eq__(self, other):
        if self.zil_key is None and other.zil_key is None:
            return self.address == other.address

        if self.zil_key is None or other.zil_key is None:
            return False

        return self.zil_key == other.zil_key

    @property
    def address0x(self) -> str:
        return "0x" + self.address

    @property
    def checksum_address(self) -> str:
        """Return str of checksum address."""
        return zilkey.to_checksum_address(self.address)

    @property
    def bech32_address(self) -> str:
        """Return str of bech32 address."""
        return zilkey.to_bech32_address(self.address)

    @property
    def public_key(self) -> Optional[str]:
        """Return str of public key."""
        return self.zil_key and self.zil_key.keypair_str.public

    @property
    def private_key(self) -> Optional[str]:
        """Return str of private key."""
        return self.zil_key and self.zil_key.keypair_str.private

    @property
    def keypair(self) -> Optional[zilkey.KeyPair]:
        """Return keypair."""
        return self.zil_key and self.zil_key.keypair_str

    @classmethod
    def from_zilkey(cls, zil_key: zilkey.ZilKey) -> "Account":
        """Init account from a ZilKey instance."""
        return cls(private_key=zil_key.encoded_private_key)

    @classmethod
    def generate(cls) -> "Account":
        """Generate new account."""
        zil_key = zilkey.ZilKey.generate_new()
        return cls.from_zilkey(zil_key)

    @classmethod
    def from_mykey_txt(cls, key_file="mykey.txt") -> "Account":
        """Load account from mykey.txt."""
        zil_key = zilkey.ZilKey.load_mykey_txt(key_file)
        return cls.from_zilkey(zil_key)

    @classmethod
    def from_keystore(cls, password: str, keystore_file: str) -> "Account":
        """Load account from keystore json file."""
        zil_key = zilkey.ZilKey.load_keystore(password, keystore_file)
        return cls.from_zilkey(zil_key)

    @classmethod
    def get_min_gas_price(cls, refresh=False) -> int:
        if refresh or cls._min_gas is None:
            cls._min_gas = int(active_chain.api.GetMinimumGasPrice())
        return cls._min_gas

    def get_balance_nonce(self) -> dict:
        """Return raw response of GetBalance."""
        resp = {"balance": 0, "nonce": 0}
        try:
            resp = active_chain.api.GetBalance(self.address)
        except APIError as e:
            if str(e) != "Account is not created":
                raise e
        return resp

    def get_balance(self) -> Zil:
        """Return account balance in Zil."""
        resp = self.get_balance_nonce()
        return Qa(resp["balance"]).toZil()

    def get_balance_qa(self) -> Qa:
        resp = self.get_balance_nonce()
        return Qa(resp["balance"])

    def get_nonce(self) -> int:
        """Return account nonce."""
        resp = self.get_balance_nonce()
        return int(resp["nonce"])

    def get_contracts(self) -> List["Contract"]:
        from pyzil.contract import Contract

        return Contract.get_contracts(self.address)

    def transfer(self, to_addr: str,
                 zils: Union[str, float, Zil, Qa],
                 nonce: Optional[int]=None,
                 gas_price: Optional[int]=None, gas_limit=1,
                 code="", data="", priority=False,
                 confirm=False, timeout=300, sleep=20):
        """Transfer zils to another address."""
        if not self.zil_key or not self.zil_key.encoded_private_key:
            raise RuntimeError("can not create transaction without private key")

        to_addr = zilkey.to_checksum_address(to_addr)
        if not to_addr:
            raise ValueError("invalid to address")

        if isinstance(zils, Qa):
            amount = zils
        else:
            if not isinstance(zils, Zil):
                zils = Zil(zils)
            amount = zils.toQa()

        if gas_price is None:
            gas_price = self.get_min_gas_price(refresh=False)

        if nonce is None:
            resp = self.get_balance_nonce()
            if amount > Qa(resp["balance"]):
                raise ValueError("insufficient balance to send")
            nonce = resp["nonce"] + 1

        params = active_chain.build_transaction_params(
            self.zil_key, to_addr,
            amount, nonce,
            gas_price, gas_limit,
            code, data, priority
        )
        self.last_params = params

        txn_info = active_chain.api.CreateTransaction(params)
        self.last_txn_info = txn_info
        if not confirm:
            return txn_info

        if not txn_info:
            return None

        txn_details = Account.wait_txn_confirm(
            txn_info["TranID"],
            timeout=timeout, sleep=sleep
        )
        self.last_txn_details = txn_details
        return txn_details

    def transfer_batch(self, batch: List[BatchTransfer],
                       gas_price: Optional[int]=None, gas_limit=1,
                       max_workers=200, timeout=None):
        """Batch Transfer zils to addresses."""
        if not self.zil_key or not self.zil_key.encoded_private_key:
            raise RuntimeError("can not create transaction without private key")

        if gas_price is None:
            gas_price = self.get_min_gas_price(refresh=False)

        resp = self.get_balance_nonce()
        batch_nonce = resp["nonce"] + 1

        txn_params = []
        for to_addr, zils in batch:
            to_addr = zilkey.to_checksum_address(to_addr)
            if not to_addr:
                raise ValueError("invalid to address")

            if isinstance(zils, Qa):
                amount = zils
            else:
                if not isinstance(zils, Zil):
                    zils = Zil(zils)
                amount = zils.toQa()

            params = active_chain.build_transaction_params(
                self.zil_key, to_addr,
                amount, batch_nonce,
                gas_price, gas_limit
            )
            txn_params.append(params)
            batch_nonce += 1

        def create_txn(p):
            try:
                txn_info = active_chain.api.CreateTransaction(p)
            except Exception as e:
                print("Error in CreateTransaction: {}".format(e))
                txn_info = None
            return txn_info

        txn_results = []
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            all_tasks = [pool.submit(create_txn, p) for p in txn_params]

            for future in futures.as_completed(all_tasks, timeout=timeout):
                try:
                    txn_results.append(future.result())
                except Exception as e:
                    print("Error: {}".format(e))
                    txn_results.append(None)

        return txn_results

    @classmethod
    def wait_txn_confirm(cls, txn_id, timeout=300, sleep=20):
        return active_chain.wait_txn_confirm(txn_id, timeout=timeout, sleep=sleep)
