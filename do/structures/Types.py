from typing import Collection, List, Union

from .VariableStructures import Variable, Outcome, Intervention

# General
V_Type = Union[Variable, Outcome, Intervention]

# Graph-related
Vertex = Union[V_Type, str]
Vertices = Collection[Vertex]
Path = List[Vertex]
