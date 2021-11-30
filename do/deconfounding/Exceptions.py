from ..core.Exceptions import ProbabilityException

class NoDeconfoundingSet(ProbabilityException):
    """
    Raised when attempting to perform a query on a set of data for which deconfounding is necessary, but no sufficient
    set of variables by which to block backdoor paths is possible.
    """
    pass
