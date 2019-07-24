#!/usr/bin/env python3

from abc import ABC, abstractmethod
from typing import Dict, Type, Optional, Callable, TypeVar, Generic, Any, cast, Union


class CoercionError(Exception):
    pass


E = TypeVar("E", bound="RingElt")  # element type


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

    def coerce(self, elt: Union[int, "RingElt"]) -> E:
        """
        Attempts to coerce the given element into this ring. If no coercion
        is found, throws "CoercionError"
        """

        # Special case: we want to treat python integers as IntegerElts
        if isinstance(elt, int):
            from integer import ZZ

            elt = ZZ(elt)

        # We can only coerce from RingElts (except the special case above)
        if not isinstance(elt, RingElt):
            raise CoercionError(f"{elt} is not a subclass of RingElt")

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

    # TODO implement coercion on operators!

    domain: Ring

    def __init__(self, domain: Ring):
        self.domain = domain

    @abstractmethod
    def __add__(self: E, other: E) -> E:
        ...

    @abstractmethod
    def __neg__(self: E) -> E:
        ...

    @abstractmethod
    def __sub__(self: E, other: E) -> E:
        ...

    @abstractmethod
    def __mul__(self: E, other: E) -> E:
        ...

    def __pow__(self: E, exp: int) -> E:
        """
        Generic powering method. Override if your class can do it more efficiently.
        """
        if exp < 0:
            raise ValueError("Generic powering only supported for exp >= 0")
        if exp == 0:
            return self.domain.ONE
        if exp == 1:
            return self

        result = self ** (exp // 2)
        result *= result
        if exp % 2 == 1:
            result *= self

        return result

    @abstractmethod
    def __eq__(self, other) -> bool:
        ...

    def is_zero(self) -> bool:
        return self == self.domain.ZERO
