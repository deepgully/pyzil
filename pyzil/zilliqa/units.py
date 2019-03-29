# -*- coding: utf-8 -*-
# Zilliqa Python Library
# Copyright (C) 2019  Gully Chen
# MIT License
"""
pyzil.zilliqa.units
~~~~~~~~~~~~

Zilliqa currencies units.

:copyright: (c) 2019 by Gully Chen.
:license: MIT License, see LICENSE for more details.
"""


class Units:
    prec = 12
    fmt = "{:.12f}"
    units = pow(10, prec)


class Qa(int):
    def __repr__(self):
        return "{} Qa".format(int(self))

    def toZil(self):
        zil = int(self) / Units.units
        return Zil(zil)

    @classmethod
    def fromZil(cls, zil):
        return Zil(zil).toQa()

    def __eq__(self, other):
        if isinstance(other, Zil):
            other = other.toQa()
        return int(self) == int(other)

    def __add__(self, other):
        """Return self + other"""
        if isinstance(other, Zil):
            other = other.toQa()
        return Qa(int(self) + int(other))

    def __radd__(self, other):
        """Return other + self"""
        if isinstance(other, Zil):
            other = other.toQa()
        return Qa(int(other) + int(self))

    def __sub__(self, other):
        """Return self - other"""
        if isinstance(other, Zil):
            other = other.toQa()
        return Qa(int(self) - int(other))

    def __rsub__(self, other):
        """Return other - self"""
        if isinstance(other, Zil):
            other = other.toQa()
        return Qa(int(other) - int(self))

    def __mul__(self, other):
        """Return self * other"""
        return Qa(int(self) * other)

    def __rmul__(self, other):
        """Return other * self"""
        return Qa(other * int(self))

    def __truediv__(self, other):
        """Return self / other"""
        return Qa(int(self) / other)

    def __rtruediv__(self, other):
        """Return other / self"""
        return Qa(other / int(self))

    def __floordiv__(self, other):
        """Return self // other"""
        return Qa(int(self) // other)

    def __rfloordiv__(self, other):
        """Return other // self"""
        return Qa(other // int(self))


class Zil(float):
    def __str__(self):
        fmt_str = Units.fmt.format(float(self))
        return fmt_str.rstrip("0").rstrip(".")

    def __repr__(self):
        return self.__str__() + " Zil"

    def __eq__(self, other):
        if not isinstance(other, Qa):
            if not isinstance(other, Zil):
                other = Zil(other)
            other = other.toQa()
        return self.toQa() == other

    def toQa(self):
        qa = float(self) * Units.units
        return Qa(int(qa))

    @classmethod
    def fromQa(cls, qa):
        return Qa(qa).toZil()

    def __add__(self, other):
        """Return self + other"""
        if isinstance(other, Qa):
            other = other.toZil()
        return Zil(float(self) + float(other))

    def __radd__(self, other):
        """Return other + self"""
        if isinstance(other, Qa):
            other = other.toZil()
        return Zil(float(other) + float(self))

    def __sub__(self, other):
        """Return self - other"""
        if isinstance(other, Qa):
            other = other.toZil()
        return Zil(float(self) - float(other))

    def __rsub__(self, other):
        """Return other - self"""
        if isinstance(other, Qa):
            other = other.toZil()
        return Zil(float(other) - float(self))

    def __mul__(self, other):
        """Return self * other"""
        return Zil(float(self) * other)

    def __rmul__(self, other):
        """Return other * self"""
        return Zil(other * float(self))

    def __truediv__(self, other):
        """Return self / other"""
        return Zil(float(self) / other)

    def __rtruediv__(self, other):
        """Return other / self"""
        return Zil(other / float(self))

    def __floordiv__(self, other):
        """Return self // other"""
        return Zil(float(self) // other)

    def __rfloordiv__(self, other):
        """Return other // self"""
        return Zil(other // float(self))


if "__main__" == __name__:
    print(Zil(0) >= 0)
