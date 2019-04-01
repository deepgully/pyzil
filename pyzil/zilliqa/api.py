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

from jsonrpcclient.exceptions import JsonRpcClientError
from jsonrpcclient.clients.http_client import HTTPClient


INVALID_PARAMS = "INVALID_PARAMS: Invalid method parameters (invalid name and/or type) recognised"


class APIError(Exception):
    pass


class ZilliqaAPI:
    """Json-RPC interface of Zilliqa APIs."""
    class APIMethod:
        def __init__(self, api: "ZilliqaAPI", method_name: str):
            self.api = api
            self.method_name = method_name

        def __call__(self, *params, **kwargs):
            resp = self.api.call(self.method_name, *params, **kwargs)
            return resp and resp.data and resp.data.result

    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.api_client = HTTPClient(self.endpoint)

    def __getattr__(self, item: str):
        return ZilliqaAPI.APIMethod(self, method_name=item)

    def call(self, method_name: str, *params, **kwargs):

        def send_request(*_params):
            try:
                return self.api_client.request(
                    method_name, *_params,
                    trim_log_values=True, **kwargs
                )
            except JsonRpcClientError as _e:
                raise APIError(_e)

        try:
            return send_request(*params)
        except APIError as e:
            # fix for jsonrpcclient < 3.3.1
            if str(e) == INVALID_PARAMS:
                if len(params) == 1 and isinstance(params[0], (dict, list)):
                    params = (list(params),)
                    return send_request(*params)
            raise e


if "__main__" == __name__:
    _api = ZilliqaAPI("https://dev-api.zilliqa.com/")
    print(_api.GetCurrentMiniEpoch())
    print(_api.GetCurrentDSEpoch())
    print(_api.GetBalance("b50c2404e699fd985f71b2c3f032059f13d6543b"))
    print(_api.GetBalance("4BAF5faDA8e5Db92C3d3242618c5B47133AE003C"))
    print(_api.GetBalance("4BAF5faDA8e5Db92C3d3242618c5B47133AE003C"))

