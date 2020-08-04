#########################################################
#                                                       #
#   Disjoint Sets                                       #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Ensure any number of sets are disjoint


def disjoint(*sets):
    return len(set().intersection(*sets)) == 0
