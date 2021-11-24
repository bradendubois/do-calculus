from typing import Collection, Sequence, Union

from .VariableStructures import Variable, Outcome, Intervention

# General
VClass = Union[Variable, Outcome, Intervention]
VMeasured = Union[Outcome, Intervention]

# Graph-related
Vertex = Union[VClass, str]
Vertices = Collection[Vertex]
Path = Sequence[str]

# TODO - Something to express a Model as different from a Graph/Table
# TODO - Something to express a query, independent from an actual model
