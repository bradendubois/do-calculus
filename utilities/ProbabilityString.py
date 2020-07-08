#########################################################
#                                                       #
#   Probability String                                  #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Helper method to convert a query into a string representation


def p_str(lhs: list, rhs: list) -> str:
    """
    Convert a head&body to a properly-formatted string
    :param lhs: The head/LHS of the query
    :param rhs: The body/RHS of the query
    :return: A string representation "P(X | Y)"
    """
    string = "P(" + ", ".join([str(var) for var in lhs])
    if rhs:
        string += " | " + ", ".join([str(var) for var in rhs])
    return string + ")"
