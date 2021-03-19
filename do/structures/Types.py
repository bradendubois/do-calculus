from typing import Collection, List, NewType, Union

from .VariableStructures import Variable, Outcome, Intervention

# General
V_Type = NewType("V_Type", Union[Variable, Outcome, Intervention])

# Graph-related
Vertex = NewType("Vertex", Union[V_Type, str])
Vertices = NewType("Vertices", Collection[Vertex])
Path = NewType("Path", List[Vertex])
