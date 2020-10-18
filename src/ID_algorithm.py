#!/usr/bin/env python

#########################################################
#                                                       #
#   ID Algorithm (WIP)                                  #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

import itertools

from probability.structures.Graph import Graph
from probability.structures.CausalGraph import CausalGraph
from util.parsers.GraphLoader import parse_graph_file_data

# Load the graph
eelworm_cg = CausalGraph(**parse_graph_file_data("./graphs/full/fumigants_eelworms.json"))


# Some boilerplate test that'll allow me to layout ID very cleanly. Maybe. Hopefully!
class ProbabilityDistribution:
    """
    A dictionary, mapping a variable to its probability distribution
    """

    def __init__(self, tables: dict):
        self.tables = tables

    def __call__(self, x):
        """
        Get subset X of some ProbabilityDistribution P.
        :param x: A set of variables in some ProbabilityDistribution P.
        :return: A ProbabilityDistribution of the subset X.
        """
        return ProbabilityDistribution({p: self.tables[p] for p in self.tables if p in x})


# Custom exception to match the ID algorithm failure
class FAIL(Exception):
    def __init__(self, g, cg):
        self.g = g
        self.cg = cg


class LatentGraph(Graph):
    """
    Represents a graph that has had its unobservable variables replaced with bidirected arcs.
    """

    def __init__(self, v, e):
        super().__init__(v, e)

        # Pre-compute all C components
        self.c_components = dict()       # Map V -> C(V)
        seen = set()        # Prevent infinite loops, just a set of vertices examined
        for vertex in v:
            if vertex in seen:  # No repeats / infinite loops
                continue

            # Initialize current C component to begin
            component = set()   # C Component is a set of vertices, can construct a subgraph
            component.add(vertex)  # C component is at least a component of 1, the original vertex
            queue = list(self.incoming[vertex] | self.outgoing[vertex])  # Start with everything connected to v

            while len(queue) > 0:
                current = queue.pop()
                if current in seen:
                    continue

                # Check if this vertex is connected by a bidirected arc to any vertex already in the component
                if any(self.bidirected(item, current) for item in component):
                    component.add(current)
                    seen.add(current)
                    # Tentatively queue all vertices connected to this vertex
                    queue = list(self.incoming[current] | self.outgoing[current])

            # Map all elements of the c-component to the set representing the full component
            for element in component:
                self.c_components[element] = component

    def __call__(self, v: set):
        """
        Compute a subset V of some Graph G.
        :param v: A set of variables in G.
        :return: A LatentGraph representing the subgraph G(V).
        """
        return LatentGraph({s for s in self.v if s in v}, {s for s in self.e if s[0] in v and s[1] in v})

    def __eq__(self, other) -> bool:
        if isinstance(other, list):     # Comparison to a C component / list of components
            return self.v == set().union(*other)    # Equality: The c components include every variable in G
        elif isinstance(other, Graph):  # Comparison to another graph
            return self.v == other.v and self.e == other.e
        return False

    def bidirected(self, s, t) -> bool:
        return (s, t) in self.e and (t, s) in self.e

    def all_c_components(self) -> list:
        no_duplicates = []
        for component in self.c_components.values():
            if component not in no_duplicates:
                no_duplicates.append(component)
        return no_duplicates


# noinspection PyPep8Naming
def latent_projection(G: Graph, U: set) -> LatentGraph:

    V = G.v.copy()
    E = set(G.e.copy())
    Un = U.copy()

    # Collapse unobservable variables, such as U1 -> U2 -> V ==> U1 -> V
    reduction = True
    while reduction:
        reduction = False

        remove = set()
        for u in Un:

            parents = [edge[0] for edge in E if edge[1] == u]       # Edges : parent -> u
            children = [edge[1] for edge in E if edge[0] == u]      # Edges : u -> child

            # All parents are unobservable, all children are observable, at least one parent
            if all(x in U for x in parents) and len(parents) > 0 and all(x not in U for x in children):
                reduction = True

                # Remove edges from parents to u
                for parent in parents:
                    E.remove((parent, u))

                # Remove edges from u to children
                for child in children:
                    E.remove((u, child))

                # Replace with edge from edge parent to each child
                for cr in itertools.product(parents, children):
                    E.add((cr[0], cr[1]))

                # U can be removed entirely from graph
                remove.add(u)

        V -= remove
        Un -= remove

    # Convert all remaining unobservable to a list to iterate through
    Un = list(Un)

    # Replace each remaining unobservable with bi-directed arcs between its children
    while len(Un) > 0:

        # Take one "current" unobservable to remove, and remove it from the graph entirely
        cur = Un.pop()
        V.remove(cur)

        assert len([edge for edge in E if edge[1] == cur]) == 0, \
            "Unobservable still had parent left."

        # All outgoing edges of this unobservable
        child_edges = {edge for edge in E if edge[0] == cur}
        E -= child_edges

        # Replace all edges from this unobservable to its children with bidirected arcs
        child_edges = list(child_edges)
        for i in range(len(child_edges)):
            a, b = child_edges[i], child_edges[(i + 1) % len(child_edges)]
            E.add((a[1], b[1]))
            E.add((b[1], a[1]))

    return LatentGraph(V, E)


# noinspection PyPep8Naming
def ID(y: set, x: set, P: ProbabilityDistribution, G: LatentGraph):

    # Helpers

    # noinspection PyPep8Naming
    def C(X: LatentGraph):
        return X.all_c_components()

    # noinspection PyPep8Naming
    def An(X):
        return G.ancestors(X)

    # noinspection PyPep8Naming
    def Sigma(*X):
        return "Sigma", *X

    # noinspection PyPep8Naming
    def Gamma(*X):
        return "Gamma", *X

    V = G.v
    empty = set()

    # ID

    # 1 - if X == {}, return Sigma_{v\y}P(v)
    if x == empty:
        return Sigma([P(v) for v in V - x])

    # 2 - if V != An(Y)_G
    #   return ID(y, x ∩ An(Y)_G, P(An(Y)), An(Y)_G)
    if V != An(y):
        return ID(y, x & An(y), P(An(y)), G(An(y)))

    # 3 - let W = (V\X) \ An(Y)_{G_X}.
    G.disable_incoming(x)
    W = (V - x) - An(y)
    G.reset_disabled()

    # if W != {}, return id_algorithm(y, x ∪ w, P, G)
    if W != empty:
        return ID(y, x | W, P, G)

    # 4 - if C(G\X) == { S_1, ..., S_k},
    #   return Sigma_{v\(y ∪ x)} Gamma_i id_algorithm(s_i, v \ s_i, P, G)
    if len(C(G(V - x))) > 1:
        # return sum([gamma([id_algorithm(s, G.v - s, P, G) for s in S]) for z in G.v - (y | x)])
        return Sigma([Gamma(ID(s, V - s, P, G)) for s in V - (y | x)])

    #   if C(G \ X) == {S},
    if len(C(G(V - x))) == 1:

        #   5 - if C(G) == {G}, throw FAIL(G, S)
        if C(G) == G:
            raise FAIL(G, C(G))

        #   6 - if S ∈ C(G), return Sigma_{S\Y} Gamma_{V_i ∈ S} P(v_i | v_P{pi}^{i -1})

        #   7 -  if (∃S')S ⊂ S' ∈ C(G)
        #       return ID(y, x ∩ S', Gamma_{V_i ∈ S'} P(V_i | V_{pi}^{i-1} ∩ S', v_{pi}^{i-1} \ S'), S')

    return
