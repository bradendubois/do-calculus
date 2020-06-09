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
