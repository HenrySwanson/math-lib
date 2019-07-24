#!/usr/bin/env python3

from itertools import zip_longest
from ring import Ring, RingElt
import collections
from typing import TypeVar, Sequence, List, Union


class PolyRingElt(RingElt):
    domain: "PolyRing"
    coeffs: List[RingElt]

    # Basics
    def __init__(self, domain: "PolyRing", coeffs: Union[RingElt, Sequence[RingElt]]):
        # Map x to [x], and then coerce all elements to the appropriate domain
        if not isinstance(coeffs, collections.Sequence):
            coeffs = [coeffs]
        coeffs = [domain.ring.coerce(x) for x in coeffs]

        # Reduce the polynomial to normal form (no leading zeros)
        zero = domain.ring.ZERO
        while coeffs and coeffs[-1] == zero:
            coeffs.pop()

        self.coeffs = coeffs

        super().__init__(domain)

    def __eq__(self, other) -> bool:
        return self.domain == other.domain and self.coeffs == other.coeffs

    def __hash__(self) -> int:
        data = (self.domain, self.coeffs)
        return hash(data)

    # Properties
    @property
    def ring(self) -> Ring:
        return self.domain.ring

    # String formatting
    def _fmt_monomial(self, a: RingElt, n: int) -> str:
        var = self.domain.var
        if n == 0:
            return f"{a}"
        elif n == 1:
            return f"{a} {var}"
        else:
            return f"{a} {var}^{n}"

    def __str__(self) -> str:
        if not self.coeffs:
            return str(self.ring.ZERO)

        return " + ".join(
            self._fmt_monomial(a, n)
            for n, a in enumerate(self.coeffs)
            if a != self.ring.ZERO
        )

    def __repr__(self) -> str:
        return str(self)

    # Arithmetic
    def __add__(self, other: "PolyRingElt") -> "PolyRingElt":
        coeffs = [
            a + b
            for a, b in zip_longest(self.coeffs, other.coeffs, fillvalue=self.ring.ZERO)
        ]
        return self.domain(coeffs)

    def __neg__(self) -> "PolyRingElt":
        return self.domain([-a for a in self.coeffs])

    def __sub__(self, other: "PolyRingElt") -> "PolyRingElt":
        coeffs = [
            a - b
            for a, b in zip_longest(self.coeffs, other.coeffs, fillvalue=self.ring.ZERO)
        ]
        return self.domain(coeffs)

    def __mul__(self, other: "PolyRingElt") -> "PolyRingElt":
        if self.is_zero() or other.is_zero():
            return self.domain.ZERO

        coeffs = [self.ring.ZERO for _ in range(self.degree() + other.degree() + 1)]
        for i, a in enumerate(self.coeffs):
            for j, b in enumerate(other.coeffs):
                coeffs[i + j] += a * b
        return self.domain(coeffs)

    def is_zero(self) -> bool:
        return not self.coeffs

    # Functions
    def degree(self) -> int:
        if not self.coeffs:
            raise ValueError("Zero polynomial has no degree")
        return len(self.coeffs) - 1


class PolyRing(Ring):
    _elt_type = PolyRingElt

    ring: Ring
    var: str

    def __init__(self, ring: Ring, var: str):
        super().__init__()

        assert len(var) == 1
        self.ring = ring
        self.var = var

        # Register coercions. We have just the one from R.
        def ring_conversion(r: RingElt) -> PolyRingElt:
            assert r.domain == self.ring
            return self(r)

        self._register_coercion(ring, ring_conversion)

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, PolyRing)
            and self.var == other.var
            and self.ring == other.ring
        )

    def variable(self) -> PolyRingElt:
        return self([0, 1])
