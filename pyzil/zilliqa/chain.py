# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License
"""
pyzil.zilliqa.chain
~~~~~~~~~~~~

Zilliqa Blockchain.

:copyright: (c) 2019 by Gully Chen.
:license: MIT License, see LICENSE for more details.
"""

import time
import logging
from typing import Union, Optional

from pyzil.common import utils
from pyzil.common.local import LocalProxy
from pyzil.zilliqa.api import ZilliqaAPI, APIError
from pyzil.crypto.zilkey import is_valid_checksum_address, ZilKey
from pyzil.zilliqa.proto import messages_pb2 as pb2


class BlockChainError(Exception):
    pass


_active_chain: Optional["BlockChain"] = None


def get_active_chain() -> "BlockChain":
    if _active_chain is None:
        raise BlockChainError("active chain is not set, please call set_active_chain first")
    return _active_chain


def set_active_chain(chain: Optional["BlockChain"]) -> None:
    global _active_chain
    _active_chain = chain


active_chain = LocalProxy(get_active_chain)


class BlockChain:
    """Zilliqa Block Chain."""
    def __init__(self, api_url: str, version: Union[str, int], network_id: Union[str, int]):
        self.api_url = api_url
        self.version = version
        self.network_id = network_id
        self.api = ZilliqaAPI(endpoint=self.api_url)

    def __str__(self):
        return "<BlockChain: {}>".format(self.api_url)

    def build_transaction_params(self, zil_key: ZilKey, to_addr: str,
                                 amount: Union[str, int], nonce: Union[str, int],
                                 gas_price: Union[str, int], gas_limit: Union[str, int],
                                 code="", data="", priority=False):

        if not is_valid_checksum_address(to_addr):
            raise ValueError("invalid checksum address")

        txn_proto = pb2.ProtoTransactionCoreInfo()
        txn_proto.version = self.version
        txn_proto.nonce = int(nonce)
        txn_proto.toaddr = utils.hex_str_to_bytes(to_addr)
        txn_proto.senderpubkey.data = zil_key.keypair_bytes.public
        txn_proto.amount.data = utils.int_to_bytes(int(amount), n_bytes=16)
        txn_proto.gasprice.data = utils.int_to_bytes(int(gas_price), n_bytes=16)
        txn_proto.gaslimit = int(gas_limit)
        if code:
            txn_proto.code = code.encode("utf-8")
        if data:
            txn_proto.data = data.encode("utf-8")

        data_to_sign = txn_proto.SerializeToString()
        signature = zil_key.sign_str(data_to_sign)
        # assert zil_key.verify(signature, data_to_sign)

        params = {
            "version": txn_proto.version,
            "nonce": txn_proto.nonce,
            "toAddr": to_addr,
            "amount": str(amount),
            "pubKey": zil_key.keypair_str.public,
            "gasPrice": str(gas_price),
            "gasLimit": str(gas_limit),
            "code": code or None,
            "data": data or None,
            "signature": signature,
            "priority": priority,
        }
        return params

    def wait_txn_confirm(self, txn_id, timeout=60, sleep=5):
        start = time.time()
        while time.time() - start <= timeout:
            try:
                return self.api.GetTransaction(txn_id)
            except APIError as e:
                logging.debug("Retry GetTransaction: {}".format(e))
                time.sleep(sleep)
        return None


TestNet = BlockChain("https://dev-api.zilliqa.com/",
                     version=21823489, network_id=333)


MainNet = BlockChain("https://api.zilliqa.com/",
                     version=65537, network_id=1)


if "__main__" == __name__:
    print(TestNet.api.GetCurrentMiniEpoch())
    print(TestNet.api.GetCurrentDSEpoch())
    print(TestNet.api.GetBalance("b50c2404e699fd985f71b2c3f032059f13d6543b"))
    print(TestNet.api.GetBalance("4BAF5faDA8e5Db92C3d3242618c5B47133AE003C"))
    print(TestNet.api.GetBalance("4BAF5faDA8e5Db92C3d3242618c5B47133AE003C"))
