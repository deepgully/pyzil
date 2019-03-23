# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License
"""
pyzil.zilliqa.api
~~~~~~~~~~~~

Json-RPC interface of Zilliqa APIs.

:copyright: (c) 2019 by Gully Chen.
:license: MIT License, see LICENSE for more details.
"""

from jsonrpcclient.clients.http_client import HTTPClient


class ZilliqaAPI:
    class APIMethod:
        def __init__(self, api, method_name):
            self.api = api
            self.method_name = method_name

        def __call__(self, *params, **kwargs):
            resp = self.api.call(self.method_name, *params, **kwargs)
            return resp and resp.data and resp.data.result

    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.api_client = HTTPClient(self.endpoint)

    def __getattr__(self, item):
        return ZilliqaAPI.APIMethod(self, method_name=item)

    def call(self, method_name, *params, **kwargs):
        if len(params) == 1 and (isinstance(params[0], (dict, list))):
            params = (list(params), )

        return self.api_client.request(
            method_name, *params,
            trim_log_values=True, **kwargs
        )


if "__main__" == __name__:
    api = ZilliqaAPI("https://dev-api.zilliqa.com/")
    print(api.GetCurrentMiniEpoch())
    print(api.GetCurrentDSEpoch())
    print(api.GetBalance("b50c2404e699fd985f71b2c3f032059f13d6543b"))
    print(api.GetBalance("4BAF5faDA8e5Db92C3d3242618c5B47133AE003C"))
    print(api.GetBalance("4BAF5faDA8e5Db92C3d3242618c5B47133AE003C"))

