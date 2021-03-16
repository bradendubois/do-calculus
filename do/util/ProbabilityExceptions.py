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


class FunctionFeedbackLoop(ProbabilityException):
    """
    Raised when some probabilistic function being evaluated encounters a feedback loop
    and will continue into a stack overflow.
    """
    pass


class ExceptionNotFired(ProbabilityException):
    """
    For use in testing; raised when we *expect* an exception to be thrown and one is not.
    """
    pass


class MissingTableRow(ProbabilityException):
    """
    Raised when a row is missing from a table and queried.
    """
    pass
