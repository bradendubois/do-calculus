from typing import Collection, Sequence, Union

from .VariableStructures import Variable, Outcome, Intervention

# General
VClass = Union[Variable, Outcome, Intervention]

# Graph-related
Vertex = Union[VClass, str]
Vertices = Collection[Vertex]
Path = Sequence[str]
