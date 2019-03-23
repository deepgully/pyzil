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

from pyzil.zilliqa.api import ZilliqaAPI


class BlockChain:
    def __init__(self, api_url, version, network_id):
        self.api_url = api_url
        self.version = version
        self.network_id = network_id
        self.api = ZilliqaAPI(endpoint=self.api_url)


TestNet = BlockChain("https://dev-api.zilliqa.com/",
                     version=21823489, network_id=333)


MainNet = BlockChain("https://api.zilliqa.com/",
                     version=65537, network_id=1)
