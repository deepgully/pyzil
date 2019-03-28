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

from typing import Union, Optional

from pyzil.common.local import LocalProxy
from pyzil.zilliqa.api import ZilliqaAPI


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
