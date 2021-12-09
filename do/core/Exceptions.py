class ProbabilityException(BaseException):
    """
    A base Exception to catch all Probability-code-related Exceptions,
    but still crash on any other Exceptions as they should be caught"
    """
    pass


class ProbabilityIndeterminableException(ProbabilityException):
    """
    A slightly more specialized Exception for indicating a failure to compute a probability, and inability to
    continue/no further options. This should never occur with a consistent model.
    """
    pass


class MissingTableRow(ProbabilityException):
    """
    Raised when a row is missing from a table, but was expected. Can occur during probability queries.
    """
    pass


class InvalidOutcome(ProbabilityException):
    """
    Raised when attempting to evaluate some query, where a given Outcome or Intervention has been assigned an outcome
    that is not possible for that respective variable.
    """
    pass



class IntersectingSets(ProbabilityException):
    """
    Raised when attempting any backdoor-path related searches, where the source, destination, and/or optional deconfounding
    set of vertices intersect.
    """
    pass



class MissingVariable(ProbabilityException):
    pass
