# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License

"""
Python Library Zilliqa APIs
~~~~~~~~~~~~~~~~~~~~~

pyzil is a Python library for Zilliqa APIs ( https://apidocs.zilliqa.com )
usage:

   >>> from pyzil.account import Account
   >>> from pyzil.zilliqa import chain
   >>> account = Account(address="b50c2404e699fd985f71b2c3f032059f13d6543b")
   >>> chain.set_active_chain(chain.TestNet)
   >>> account.get_balance()
   610.269 Zil
   >>> account.get_nonce()
   3
   >>> chain.set_active_chain(chain.MainNet)
   >>> account.get_balance()
   0 Zil

:copyright: (c) 2019 by Gully Chen.
:license: MIT License, see LICENSE for more details.
"""

version = "0.5.23"
