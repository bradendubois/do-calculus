#########################################################
#                                                       #
#   Probability Exceptions                              #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################


class ProbabilityException(Exception):
    """
    A base Exception to catch all Probability-code-related Exceptions,
    but still crash on any other Exceptions as they should be caught"
    """
    pass


class ProbabilityIndeterminableException(ProbabilityException):
    """
    A slightly more specialized Exception for indicating a failure
    to compute a probability, and inability to continue/no further
    options
    """
    pass


class NotFunctionDeterminableException(ProbabilityException):
    """
    Raised when a Variable is attempted to be calculated by a
    probabilistic function when there is not one.
    """
    pass


# TODO - Some kind of exception here to indicate when a given test SHOULD crash, but didn't?
