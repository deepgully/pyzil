# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License
"""
pyzil.zilliqa.node
~~~~~~~~~~~~

Zilliqa Node API.

:copyright: (c) 2019 by Gully Chen.
:license: MIT License, see LICENSE for more details.
"""

import socket
from jsonrpcclient.clients.socket_client import SocketClient


class Node:
    """Zilliqa Node API."""
    class NodeMethod:
        def __init__(self, node: "Node", method_name: str):
            self.node = node
            self.method_name = method_name

        def __call__(self, *params, **kwargs):
            resp = self.node.call(self.method_name, *params, **kwargs)
            return resp and resp.data and resp.data.result

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def __str__(self):
        return "<Node {}:{}>".format(self.host, self.port)

    def __getattr__(self, item: str):
        return Node.NodeMethod(self, method_name=item)

    def call(self, method_name: str, *params, **kwargs):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))

        try:
            api_client = SocketClient(sock)
            return api_client.request(
                method_name, *params,
                trim_log_values=True, **kwargs
            )
        finally:
            sock.close()


LocalNode = Node("127.0.0.1", 4201)


if "__main__" == __name__:
    print(LocalNode.GetCurrentMiniEpoch())
    print(LocalNode.GetCurrentDSEpoch())
    print(LocalNode.GetNodeType())
    print(LocalNode.GetDSCommittee())
    print(LocalNode.GetNodeState())
    print(LocalNode.IsTxnInMemPool("txn_id"))
