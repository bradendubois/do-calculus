from itertools import chain, combinations
from typing import Collection, Iterator, Union

from .Types import Intervention, Outcome, Vertex


def power_set(variable_list: list or set, allow_empty_set=True) -> Iterator[any]:
    """
    Quick helper that creates a chain of tuples, which will be the power set of the given list or set
    @param variable_list: Any arbitrary list or set
    @param allow_empty_set: Whether or not to consider the empty set {} as a valid set
    @return: A chain object of tuples; power set of variable_list
    """
    p_set = list(variable_list)
    base = 0 if allow_empty_set else 1
    return chain.from_iterable(combinations(p_set, r) for r in range(base, len(p_set)+1))


def minimal_sets(*sets) -> list:
    """
    Take a set of sets, and return only the minimal sets
    @param sets: An arbitrary number of sets, each set containing strings
    @return: A list of minimal sets; that is, all sets such that there is no superset
    """
    sorted_sets = sorted(map(set, list(sets)), key=len)
    minimal_subsets = []
    for s in sorted_sets:
        if not any(minimal_subset.issubset(s) for minimal_subset in minimal_subsets):
            minimal_subsets.append(s)
    return minimal_subsets


def disjoint(*sets) -> bool:
    """
    Check whether or not an arbitrary number of sets are completely disjoint; that is, no element in any set exists in
    any other given set.
    @param sets: Any number of sets.
    @return: True if all sets are disjoint, False otherwise
    """
    return len(set().union(*sets)) == sum(map(lambda iterable: len(iterable), sets))


def within_precision(a: float, b: float) -> bool:
    """
    Check whether two values differ by an amount less than some number of digits of precision
    @param a: The first value
    @param b: The second value
    @return: True if the values are within the margin of error acceptable, False otherwise
    """
    return abs(a - b) < 1 / (10 ** 8)
