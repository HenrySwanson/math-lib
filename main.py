#!/usr/bin/env python3

from integer import ZZ
from zmod import ZMod
from poly import PolyRing
from ring import RingProperties


def hom_tests(ring):
    assert ring.ZERO == ring(0)
    assert ring.ONE == ring(1)

    for a, b in [(3, 50), (0, 4), (-4, -5)]:
        assert ring(a) + ring(b) == ring(a + b)
        assert ring(a) - ring(b) == ring(a - b)
        assert ring(a) * ring(b) == ring(a * b)
        assert -ring(a) == ring(-a)


# Integer tests
# TODO

# ZMod tests
Z23 = ZMod(23)
hom_tests(Z23)

assert Z23(25) == Z23(2)
assert Z23(-5) == Z23(18)
assert Z23(8) / Z23(4) == Z23(2)

assert Z23(5).inv() == Z23(-9)
assert Z23(6) / Z23(5) == Z23(-9 * 6)

assert Z23(4) ** 3 == Z23(64)
assert Z23(4) ** -1 == Z23(6)


Z22 = ZMod(22)
hom_tests(Z22)

assert Z22(7).has_inv()
assert not Z22(6).has_inv()


# Poly tests
Zx = PolyRing(ZZ, "x")
hom_tests(Zx)

x = Zx.variable()
assert Zx(4) == Zx([4])
assert Zx([4, 5]) == Zx(4) + Zx(5) * x
assert Zx([-4, 0, 0, 1]) == x ** 3 - Zx(4)

assert Zx([1, 1]) * Zx([-1, 1]) == Zx([-1, 0, 1])
assert Zx([3, 2, 1, 5]).degree() == 3
assert Zx(4).degree() == 0
try:
    Zx(0).degree()
    assert False
except ValueError:
    pass


# Putting it together (also some string tests)
R = PolyRing(ZMod(5), "x")
x = R.variable()

hom_tests(R)

assert str(R.ZERO) == "0"
assert str(R.ONE) == "1"
assert str(R([1, 2, -3])) == "1 + 2 x + 2 x^2"
assert str(R([])) == "0"
assert str(R([1])) == "1"

# Testing coercion methods
a = ZZ(3)
assert a == 3

assert a + 4 == 7
assert a - 7 == -4
assert a * 2 == 6
assert 1 + a == 4
assert 2 - a == -1
assert 9 * a == 27

b = Z23(7)
assert b == 7
assert b == 30
assert a + b == 10
assert a * b == -2

c = Zx([1, 2, 3])
assert c - 2 == Zx([-1, 2, 3])
assert c * 3 == Zx([3, 6, 9])

# Testing properties
assert not ZZ._props[RingProperties.FINITE]
assert not ZZ._props[RingProperties.FIELD]
assert ZZ._props[RingProperties.ORDERED]

assert Z23._props[RingProperties.FINITE]
assert Z23._props[RingProperties.FIELD]
assert not Z23._props[RingProperties.ORDERED]

assert Z22._props[RingProperties.FINITE]
assert not Z22._props[RingProperties.FIELD]
assert not Z22._props[RingProperties.ORDERED]

assert not Zx._props[RingProperties.FINITE]
assert not Zx._props[RingProperties.FIELD]
assert Zx._props[RingProperties.ORDERED]

# recall R is Z5[x]
assert not R._props[RingProperties.FINITE]
assert not R._props[RingProperties.FIELD]
assert not R._props[RingProperties.ORDERED]
