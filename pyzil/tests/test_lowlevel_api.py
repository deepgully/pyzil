# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License

import pytest

from pprint import pprint
from pyzil.zilliqa.api import ZilliqaAPI, APIError


class TestAPI:
    def test_blockchain_apis(self):
        api = ZilliqaAPI("https://dev-api.zilliqa.com/")
        print(api)
        assert api.GetNetworkId() == "333"

        info = api.GetBlockchainInfo()
        pprint(info)
        assert info is not None
        assert "CurrentDSEpoch" in info
        assert "CurrentMiniEpoch" in info

        sharding = api.GetShardingStructure()
        pprint(sharding)
        assert sharding is not None
        assert "NumPeers" in sharding

        ds_block_info = api.GetDsBlock("20")
        pprint(ds_block_info)
        assert ds_block_info

        ds_block_info = api.GetLatestDsBlock()
        pprint(ds_block_info)
        assert ds_block_info

        num_ds_blocks = api.GetNumDSBlocks()
        pprint(num_ds_blocks)
        assert num_ds_blocks

        ds_block_rate = api.GetDSBlockRate()
        pprint(ds_block_rate)
        assert ds_block_rate

        ds_blocks = api.DSBlockListing(1)
        pprint(ds_blocks)
        assert ds_blocks
        assert len(ds_blocks["data"]) == 10

        tx_block_info = api.GetTxBlock("1")
        pprint(tx_block_info)
        assert tx_block_info

        tx_block_info = api.GetLatestTxBlock()
        pprint(tx_block_info)
        assert tx_block_info

        num_tx_blocks = api.GetNumTxBlocks()
        pprint(num_tx_blocks)
        assert num_tx_blocks

        tx_block_rate = api.GetTxBlockRate()
        pprint(tx_block_rate)
        assert tx_block_rate

        tx_blocks = api.TxBlockListing(1)
        pprint(tx_blocks)
        assert tx_blocks
        assert len(tx_blocks["data"]) == 10

        num_txns = api.GetNumTransactions()
        pprint(num_txns)
        assert num_txns

        txn_rate = api.GetTransactionRate()
        pprint(txn_rate)

        tx_block = api.GetCurrentMiniEpoch()
        pprint(tx_block)
        assert tx_block

        ds_block = api.GetCurrentDSEpoch()
        pprint(ds_block)
        assert ds_block

        shard_diff = api.GetPrevDifficulty()
        pprint(shard_diff)
        assert shard_diff

        ds_diff = api.GetPrevDSDifficulty()
        pprint(ds_diff)
        assert ds_diff

    def test_transaction_apis(self):
        api = ZilliqaAPI("https://dev-api.zilliqa.com/")
        print(api)
        assert api.GetNetworkId() == "333"

        latest_txns = api.GetRecentTransactions()
        pprint(latest_txns)

        if latest_txns:
            txn_hash = latest_txns["TxnHashes"][0]
            txn_info = api.GetTransaction(txn_hash)
            pprint(txn_info)
            assert txn_info

            tx_block = txn_info["receipt"]["epoch_num"]
            txns = api.GetTransactionsForTxBlock(tx_block)
            pprint(txns)
            assert txns

        num_txns = api.GetNumTxnsTxEpoch()
        pprint(num_txns)
        assert num_txns

        num_txns = api.GetNumTxnsDSEpoch()
        pprint(num_txns)
        assert num_txns

        gas_price = api.GetMinimumGasPrice()
        pprint(gas_price)
        assert gas_price

    def test_contract_apis(self):
        pass

    def test_account_apis(self):
        api = ZilliqaAPI("https://dev-api.zilliqa.com/")
        print(api)
        assert api.GetNetworkId() == "333"

        balance = api.GetBalance("b50c2404e699fd985f71b2c3f032059f13d6543b")
        pprint(balance)
        assert "balance" in balance
        assert "nonce" in balance

        with pytest.raises(APIError):
            api.GetBalance("b50c2404e699fd985f71b2c3f032059f13d6543c")




