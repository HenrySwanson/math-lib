#!/usr/bin/env python3

from abc import ABC, abstractmethod
from typing import (
    Dict,
    Type,
    Optional,
    Callable,
    TypeVar,
    Generic,
    Any,
    cast,
    Union,
    Tuple,
)


E = TypeVar("E", bound="RingElt")  # element type
RingEltPlus = Union[int, "RingElt"]  # RingElt plus some special cases


class CoercionError(Exception):
    pass


def to_elt(x: RingEltPlus) -> "RingElt":
    # If it's already an element, return it
    if isinstance(x, RingElt):
        return x

    # Special case: we want to treat python integers as IntegerElts
    if isinstance(x, int):
        from integer import ZZ

        return ZZ(x)

    raise CoercionError(
        f"{x} (type {x.__class__}) could not be interpreted as a RingElt"
    )


class Ring(ABC, Generic[E]):
    """
    An object of type Ring represents a ring.
    """

    _elt_type: Type[E]  # TODO maybe change into _element_constructor?
    _coerce_maps: Dict["Ring", Callable[[Any], E]]

    def __init__(self, *args, **kwargs):
        self._coerce_maps = {}

    def __call__(self, *args, **kwargs) -> E:
        # note that we pass ourselves in as the domain; this isn't a pass-thru!
        return self._elt_type(self, *args, **kwargs)  # type: ignore

    def coerce(self, elt: RingEltPlus) -> E:
        """
        Attempts to coerce the given element into this ring. If no coercion
        is found, throws "CoercionError"
        """

        # Turn our special cases into actual elements
        elt = to_elt(elt)

        # If it's our own type, just return it
        if elt.domain == self:
            return cast(E, elt)

        # For each coercion pathway into this ring...
        for source, coercion_map in self._coerce_maps.items():
            try:
                # ...see if we can coerce the element into the source of that path.
                # If so, apply coercion map and return.
                return coercion_map(source.coerce(elt))
            except CoercionError:
                pass

        # Looks like we can't coerce.
        raise CoercionError(f"Unable to coerce {elt} by any path")

    def _register_coercion(self, from_ring: "Ring", map: Callable[[Any], E]):
        self._coerce_maps[from_ring] = map

    @property
    def ZERO(self) -> E:
        return self.coerce(0)

    @property
    def ONE(self) -> E:
        return self.coerce(1)


class RingElt(ABC):

    domain: Ring

    def __init__(self, domain: Ring):
        self.domain = domain

    @staticmethod
    def _coerce_pair(lhs: RingEltPlus, rhs: RingEltPlus) -> Tuple["RingElt", "RingElt"]:
        lhs = to_elt(lhs)
        rhs = to_elt(rhs)

        try:
            return lhs, lhs.domain.coerce(rhs)
        except CoercionError:
            pass

        try:
            return rhs.domain.coerce(lhs), rhs
        except CoercionError:
            pass

        raise CoercionError(
            f"Could not find a common parent for {lhs.domain} and {rhs.domain}"
        )

    # Magic methods; use coercion to apply single-underscore methods
    def __add__(self, other: RingEltPlus) -> "RingElt":
        lhs, rhs = RingElt._coerce_pair(self, other)
        return lhs._add_(rhs)

    def __radd__(self, other: RingEltPlus) -> "RingElt":
        rhs, lhs = RingElt._coerce_pair(self, other)
        return lhs._add_(rhs)

    def __neg__(self) -> "RingElt":
        return self._neg_()

    def __sub__(self, other: RingEltPlus) -> "RingElt":
        lhs, rhs = RingElt._coerce_pair(self, other)
        return lhs._sub_(rhs)

    def __rsub__(self, other: RingEltPlus) -> "RingElt":
        rhs, lhs = RingElt._coerce_pair(self, other)
        return lhs._sub_(rhs)

    def __mul__(self, other: RingEltPlus) -> "RingElt":
        lhs, rhs = RingElt._coerce_pair(self, other)
        return lhs._mul_(rhs)

    def __rmul__(self, other: RingEltPlus) -> "RingElt":
        rhs, lhs = RingElt._coerce_pair(self, other)
        return lhs._mul_(rhs)

    def __pow__(self, exp: int) -> "RingElt":
        return self._pow_(exp)

    def __eq__(self, other: RingEltPlus) -> bool: # type: ignore
        # TODO can i do a isinstance on type aliases? then i can make this
        # signature "object" and drop the type ignore
        lhs, rhs = RingElt._coerce_pair(self, other)
        return lhs._eq_(rhs)

    # Required things to implement to be a ring
    @abstractmethod
    def _add_(self: E, other: E) -> E:
        ...

    @abstractmethod
    def _neg_(self: E) -> E:
        ...

    @abstractmethod
    def _sub_(self: E, other: E) -> E:
        ...

    @abstractmethod
    def _mul_(self: E, other: E) -> E:
        ...

    def _pow_(self: E, exp: int) -> E:
        """
        Generic powering method. Override if your class can do it more efficiently.
        """
        if exp < 0:
            raise ValueError("Generic powering only supported for exp >= 0")
        if exp == 0:
            return self.domain.ONE
        if exp == 1:
            return self

        result = self._pow_(exp // 2)
        result = result._mul_(result)
        if exp % 2 == 1:
            result = result._mul_(self)

        return result

    @abstractmethod
    def _eq_(self, other) -> bool:
        ...

    def is_zero(self) -> bool:
        return self == self.domain.ZERO
