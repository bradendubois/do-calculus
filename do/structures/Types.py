from typing import Collection, Sequence, Union

from .VariableStructures import Variable, Outcome, Intervention

# General
V_Type = Union[Variable, Outcome, Intervention]

# Graph-related
Vertex = Union[V_Type, str]
Vertices = Collection[Vertex]
Path = Sequence[str]


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


class MissingTableRow(ProbabilityException):
    """
    Raised when a row is missing from a table and queried.
    """
    pass
