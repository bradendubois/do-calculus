#########################################################
#                                                       #
#   Minimize Sets                                       #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Reduce a collection of sets to a list of minimal sets


def minimal_sets(set_of_sets: list) -> list:
    """
    Take a set of sets, and return only the minimal sets
    :param set_of_sets: A set of sets, each set containing strings
    :return: A list of minimal sets
    """
    sorted_sets = sorted(map(set, set_of_sets), key=len)
    minimal_subsets = []
    for s in sorted_sets:
        if not any(minimal_subset.issubset(s) for minimal_subset in minimal_subsets):
            minimal_subsets.append(s)
    return minimal_subsets
