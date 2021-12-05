from typing import Collection, Optional

from ..core.Expression import Expression
from ..core.Graph import Graph
from ..core.Model import Model
from ..core.Types import Vertex, Path
from ..core.Variables import Intervention

from .Backdoor import backdoors, deconfound
from .Do import treat


class API:

    def treat(self, expression: Expression, interventions: Collection[Intervention], model: Model) -> float:
        return treat(expression, interventions, model)

    def backdoors(self, x: Collection[Vertex], y: Collection[Vertex], graph: Graph, z: Optional[Collection[Vertex]] = None) -> Collection[Path]:
        return backdoors(x, y, graph, z)

    def blocks(self, x: Collection[Vertex], y: Collection[Vertex], graph: Graph, z: Collection[Vertex]) -> bool:
        return len(backdoors(x, y, graph, z)) == 0

    def deconfound(self, x: Collection[Vertex], y: Collection[Vertex], graph: Graph) -> Collection[Collection[Vertex]]:
        return deconfound(x, y, graph)
