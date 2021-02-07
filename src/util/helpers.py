from itertools import chain, combinations
from typing import Iterator


def power_set(variable_list, allow_empty_set=True) -> Iterator[any, any]:
    """
    Quick helper that creates a chain of tuples, which will be the power set of the given list
    @param variable_list: A list of string variables
    @param allow_empty_set: Whether or not to consider the empty set {} as a valid set
    @return: A chain object of tuples; power set of variable_list
    """
    p_set = list(variable_list)
    base = 0 if allow_empty_set else 1
    return chain.from_iterable(combinations(p_set, r) for r in range(base, len(p_set)+1))


def minimal_sets(set_of_sets: list) -> list:
    """
    Take a set of sets, and return only the minimal sets
    @param set_of_sets: A set of sets, each set containing strings
    @return: A list of minimal sets
    """
    sorted_sets = sorted(map(set, set_of_sets), key=len)
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
    return len(set().intersection(*sets)) == 0
