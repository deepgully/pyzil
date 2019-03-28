# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License

import pytest
from pprint import pprint

from pyzil.zilliqa import chain
from pyzil.zilliqa.chain import active_chain


class TestChain:
    def test_active_chain(self):
        chain.set_active_chain(None)
        with pytest.raises(chain.BlockChainError):
            active_chain.api.GetCurrentDSEpoch()

        chain.set_active_chain(chain.MainNet)
        print(active_chain)

        chain.set_active_chain(chain.TestNet)
        print(active_chain)

        resp = active_chain.api.GetCurrentDSEpoch()
        pprint(resp)
        assert resp

