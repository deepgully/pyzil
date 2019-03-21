# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License
"""
pyzil.crypto.tools
~~~~~~~~~~~~

crypto tools

:copyright: (c) 2019 by Gully Chen.
:license: MIT License, see LICENSE for more details.
"""

import hashlib


def hash256_bytes(*bytes_hex, encoding="utf-8") -> bytes:
    m = hashlib.sha256()
    for b in bytes_hex:
        if isinstance(b, str):
            b = b.encode(encoding=encoding)
        m.update(b)
    return m.digest()


def hash256_str(*bytes_hex, encoding="utf-8") -> str:
    m = hashlib.sha256()
    for b in bytes_hex:
        if isinstance(b, str):
            b = b.encode(encoding=encoding)
        m.update(b)
    return m.hexdigest()
