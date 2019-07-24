#!/usr/bin/env python3

from typing import List


def is_prime(n: int) -> bool:
    # TODO do something better
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    r = 3
    while r * r <= n:
        if n % r == 0:
            return False
        r += 2
    return True


def get_factor(n: int) -> int:
    if n % 2 == 0:
        return 2
    r = 3
    while r * r <= n:
        if n % r == 0:
            return r
    return n  # n must be prime


def factorize(n: int) -> List[int]:
    factors = []
    while n != 1:
        k = get_factor(n)
        factors.append(k)
        n //= k
    factors.sort()
    return factors
