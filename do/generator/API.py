from typing import Mapping, Optional, Sequence

from ..core.Graph import Graph


class API:

    def generate_graph(self, num_vertices: int, min_edges: int, max_edges: int, subgraphs = False) -> Optional[Graph]:
        ...

    def generate_distribution(self, graph: Graph, outcomes: Optional[Mapping[str, Sequence[str]]]):
        ...
