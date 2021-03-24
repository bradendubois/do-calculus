from typing import Collection, Sequence, Union

from .VariableStructures import Variable, Outcome, Intervention

# General
V_Type = Union[Variable, Outcome, Intervention]

# Graph-related
Vertex = Union[V_Type, str]
Vertices = Collection[Vertex]
Path = Sequence[str]
