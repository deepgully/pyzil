# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License

from pyzil.zilliqa.units import Zil, Qa


class TestUnits:
    def test_units(self):
        zil = Zil(1000.123)
        print(zil)
        print(repr(zil))
        assert zil == Zil("1000.123")

        qa = Qa(1000123000000000)
        print(qa)
        print(repr(qa))
        assert qa == zil
        assert zil == qa

        assert zil + 100 == Zil(1000.123 + 100)
        assert zil + 99.999 < Zil(1000.123 + 100)
        assert zil + 100.000000000001 > Zil(1000.123 + 100)
        assert zil + 100.0000000000001 == Zil(1000.123 + 100)

        assert zil + 0.000000000001 == Zil(1000.123) + Qa(1)
        assert zil + 0.000000001001 == Zil(1000.123) + Qa(1001)

        assert zil - 0.000000000001 == Zil(1000.123) - Qa(1)
        assert zil - Zil(0.000000001001) == Zil(1000.123) - Qa(1001)

        zil = Zil(1000000000.000000000001)
        print(zil)
        print(repr(zil))
        assert zil * 2 == zil * 2.0
        assert zil * 2 == Zil(2000000000.000000000002)

        print(zil / 3)
        print(repr(zil / 3))
        assert zil / 3.0 == zil / 3
        assert zil / 2.0 == Zil("500000000")

        zil = Zil(1000000000.99)
        print(zil / 2.0)
        print(repr(zil / 2.0))
        assert zil / 2.0 == Zil("500000000.495")
        assert zil / 2.0 == Zil(500000000.495)

        assert zil // 2.0 == Zil("500000000")
        assert zil // 2.0 == Zil(500000000)

        zil = Zil("3.65")
        assert zil == Zil(3.65)
        assert zil == Qa(3650000000000)
        assert zil == Qa(3650000000001) - Qa(1)
        print("{:.12f}".format(zil), zil)
        print(repr(zil))

        print(Zil(1234566789215.987654321))
        print(repr(Zil(1234566789215.987654321)))


