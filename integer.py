#!/usr/bin/env python3

from ring import Ring, RingElt
from typing import Union

# TODO maybe just virtual subclass this so this isn't so snowflakey
class IntegerElt(RingElt):

    domain: "_IntegerSingleton"
    value: int

    def __init__(self, domain: "_IntegerSingleton", value: "IntType"):
        self.value = value if isinstance(value, int) else value.value
        super().__init__(domain)

    # TODO can i omit these?
    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return str(self)

    def __int__(self) -> int:
        return self.value

    def __add__(self, other: "IntegerElt") -> "IntegerElt":
        return self.domain(self.value + other.value)

    def __neg__(self) -> "IntegerElt":
        return self.domain(-self.value)

    def __sub__(self, other: "IntegerElt") -> "IntegerElt":
        return self.domain(self.value - other.value)

    def __mul__(self, other: "IntegerElt") -> "IntegerElt":
        return self.domain(self.value * other.value)

    def __eq__(self, other) -> bool:
        return self.value == other.value


class _IntegerSingleton(Ring):
    # this is a singleton immutable class, i.e., we have no state

    _elt_type = IntegerElt

    def __eq__(self, other) -> bool:
        return isinstance(other, _IntegerSingleton)

    def __hash__(self) -> int:
        return hash("ZZ")  # some string

    @property
    def ZERO(self) -> "IntegerElt":
        return IntegerElt(self, 0)

    @property
    def ONE(self) -> "IntegerElt":
        return IntegerElt(self, 1)


# Things for export
ZZ = _IntegerSingleton()
IntType = Union[int, IntegerElt]
