#########################################################
#                                                       #
#   LatentGraph                                         #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

from random import choice
from typing import Set

from ...structures.Graph import Graph

# A representation of a Latent Graph, in which we have replaced all unobservable
#   variables with bidirected arcs between the observable variables


class CComponent(set):

    def __init__(self, v: Set[str]):
        super(CComponent, self).__init__()
        self.v = v

    def __hash__(self):
        return sum(map(hash, self.v))

    def __str__(self):
        return str(self.v)


class LatentGraph(Graph):
    """
    Represents a graph that has had its unobservable variables replaced with bidirected arcs.
    """

    def __init__(self, v, e):
        super().__init__(v, e)

        # Pre-compute all C components
        self.c_components = dict()       # Map V -> C(V)

        all_components = self._all_c_components()
        for component in all_components:
            for v in component.v:
                self.c_components[v] = component

    def _all_c_components(self):

        all_c_components = set()

        v_working = self.v.copy()

        while len(v_working):

            start = choice(list(v_working))
            component = set()
            queue = [start]

            while len(queue):
                c = queue.pop()
                component.add(c)

                for other in v_working - ({c} | component):
                    if self.bidirected(c, other):
                        queue.append(other)

            v_working -= component

            all_c_components.add(CComponent(component))

        assert len(v_working) == 0
        return all_c_components

    def __getitem__(self, v: set):
        """
        Compute a subset V of some Graph G.
        :param v: A set of variables in G.
        :return: A LatentGraph representing the subgraph G(V).
        """
        return LatentGraph({s for s in self.v if s in v}, {s for s in self.e if s[0] in v and s[1] in v})

    def __eq__(self, other) -> bool:
        if isinstance(other, list) and len(other) == 1:     # Comparison to a C component
            return self.v == set(other[0])     # Equality: The c component includes every variable in G
        elif isinstance(other, Graph):  # Comparison to another graph
            return self.v == other.v and self.e == other.e
        return False

    def bidirected(self, s, t) -> bool:
        return (s, t) in self.e and (t, s) in self.e

    def all_c_components(self) -> list:
        return list(map(lambda c: c.v, set(self.c_components.values())))
