#########################################################
#                                                       #
#   Custom Set Functions                                #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# We can't use the custom Set methods for union, difference, etc. because of the use of renamed Variables.
#   Need to be able to tell that X' === X, but {X', Y} - {X} == {"Y"}


def union(s1: set, s2: set) -> set:
    """
    Union two sets that may contain renamed Variables
    :param s1: Set 1
    :param s2: Set 2
    :return: A new set, merged without duplicates arising from renamed Variables
    """

    # New set to add everything to
    new_set = set()

    # Only add a relabelled variable into the set if it is
    # the first occurrence of this variable at all
    for i in s1:
        if clean(i) not in new_set:
            new_set.add(i)

    for i in s2:
        if clean(i) not in new_set:
            new_set.add(i)

    return new_set


def subtract(s1: set, s2: set) -> set:
    """
    Take the difference between two sets, accounting for renamed Variables
    :param s1: Set 1
    :param s2: Set 2
    :return: s1 - s2
    """

    new_set = set()
    clean_s2 = clean(s2)

    # Anything in s1 can remain, if it cleaned is not in s2, cleaned
    for i in s1:
        if clean(i) not in clean_s2:
            new_set.add(i)

    return new_set


def rename(s: set or str) -> set or str:
    """
    "Rename" is to always add a tick, ', to a string.
    :param s: A set or string, all of which to rename
    :return:
    """
    if isinstance(s, str):
        return s + "'"
    return {item + "'" for item in s}


def clean(s: set or str) -> set or str:
    """
    "Clean", or remove all the ticks, ', off any number of renamed variables.
    :param s:
    :return:
    """
    if isinstance(s, str):
        return s.strip("'")
    return {item.strip("'") for item in s}
