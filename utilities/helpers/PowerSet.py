#########################################################
#                                                       #
#   PowerSet                                            #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

import itertools        # Used for power set / product creation


def power_set(variable_list, allow_empty_set=True):
    """
    Quick helper that creates a chain of tuples, which will be the power set of the given list
    :param variable_list: A list of string variables
    :param allow_empty_set: Whether or not to consider the empty set {} as a valid set
    :return: A chain object of tuples; power set of variable_list
    """
    p_set = list(variable_list)
    base = 0 if allow_empty_set else 1
    return itertools.chain.from_iterable(itertools.combinations(p_set, r) for r in range(base, len(p_set)+1))
