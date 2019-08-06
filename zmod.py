#!/usr/bin/env python3

from math import gcd
from ring import Ring, RingElt, RingProperties
from typing import Iterator

from integer import ZZ, IntegerElt, IntType
from util import is_prime


class ZModElt(RingElt):
    domain: "ZMod"  # parent ring
    value: int  # value in [0, n)

    # Basics
    def __init__(self, domain: "ZMod", value: IntType) -> None:
        super().__init__(domain)
        self.value = int(value) % self.domain.n

    def _eq_(self, other: "ZModElt") -> bool:
        return self.value == other.value

    def __hash__(self) -> int:
        data = (self.domain, self.value)
        return hash(data)

    # String formatting
    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return str(self)

    # Arithmetic
    def _add_(self, other: "ZModElt"):
        return self.domain(self.value + other.value)

    def _neg_(self: "ZModElt"):
        return self.domain(-self.value)

    def _sub_(self, other: "ZModElt"):
        return self.domain(self.value - other.value)

    def _mul_(self, other: "ZModElt"):
        return self.domain(self.value * other.value)

    def __truediv__(self, other):
        return self * other.inv()

    def _pow_(self, exp: int):
        if exp >= 0:
            a = self.value
            b = exp
        else:
            a = self.inv().value
            b = -exp
        return self.domain(pow(a, b, self.domain.n))

    def has_inv(self) -> bool:
        return gcd(self.domain.n, self.value) == 1

    def inv(self) -> "ZModElt":
        # Extended GCD
        # Let n = ring modulus, a = self.value
        n = self.domain.n
        a = self.value

        # Do the usual sequence of remainders r that you get when computing a
        # GCD. But also, construct a parallel sequence s such that at each
        # step, a*s = r mod n.

        # Start with r = [n, a], s = [0, 1], end with r = 1, s = a^-1
        r, r_ = n, a
        s, s_ = 0, 1
        while r_ != 0:
            # If r = qr' + r'', then set s'' = s - qs'. Then
            #    a(s - qs') = as - qas' = r - qr' = r''
            q = r // r_
            r, r_ = (r_, r - q * r_)
            s, s_ = (s_, s - q * s_)
        if r != 1:
            raise ZeroDivisionError(f"{a} has no inverse mod {n}")
        return self.domain(s)


class ZMod(Ring):
    _elt_type = ZModElt

    n: int

    def __init__(self, n: IntType) -> None:
        super().__init__()

        self.n = int(n)
        assert n >= 1

        self._props[RingProperties.FINITE] = True
        self._props[RingProperties.FIELD] = is_prime(n)
        self._props[RingProperties.ORDERED] = False

        # Register coercions. Only one we've got is from ZZ.
        def ZZ_coercion(x: IntegerElt) -> ZModElt:
            return self(x.value)

        self._register_coercion(ZZ, ZZ_coercion)

    def __eq__(self, other) -> bool:
        return isinstance(other, ZMod) and self.n == other.n

    def __hash__(self) -> int:
        return hash(self.n)

    def __iter__(self) -> Iterator["ZModElt"]:
        return iter(self(a) for a in range(self.n))
