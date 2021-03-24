class ProbabilityException(BaseException):
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


class MissingTableRow(ProbabilityException):
    """
    Raised when a row is missing from a table and queried.
    """
    pass


class InvalidOutcome(ProbabilityException):
    pass


class NoDeconfoundingSet(ProbabilityException):
    pass


class IntersectingSets(ProbabilityException):
    pass