from itertools import product
from typing import Collection, Dict, Optional, Union

from ..core.ConditionalProbabilityTable import ConditionalProbabilityTable
from ..core.Expression import Expression
from ..core.Model import Model
from ..core.Types import Vertex, Path
from ..core.Variables import Intervention, Outcome, Variable, parse_outcomes_and_interventions

from .Backdoor import BackdoorController
from .Do import CausalGraph


class API:

    def treat(self, expression: Expression, interventions: Collection[Intervention], model: Model) -> float:
        ...

    def backdoors(self, x: Union[Vertex, Collection[Vertex]], y: Union[Vertex, Collection[Vertex]]) -> Collection[Path]:
        ...

    def deconfound(self, x: Union[Vertex, Collection[Vertex]], y: Union[Vertex, Collection[Vertex]]) -> Collection[Collection[Vertex]]:
        ...
    
    def blocks(self, x: Union[Vertex, Collection[Vertex]], y: Union[Vertex, Collection[Vertex]], z: Union[Vertex, Collection[Vertex]]) -> bool:
        ...
