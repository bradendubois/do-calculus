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

    def __init__(self, tables: dict, given=None):
        self.tables = tables
        self.given = given

    def __call__(self, x, parents=None):
        """
        Get subset X of some ProbabilityDistribution P.
        :param x: A set of variables in some ProbabilityDistribution P.
        :param parents: The set of parents of X
        :return: A ProbabilityDistribution of the subset X.
        """

        # Line 1 Return
        if isinstance(x, str) and parents is None:
            return ProbabilityDistribution({x: self.tables[x]})

        # Line 2 Return
        elif isinstance(x, set) and parents is None:
            return ProbabilityDistribution({p: self.tables[p] for p in self.tables if p in x})

        # Line 6 return
        elif isinstance(x, str) and parents is not None:
            return ProbabilityDistribution({x: self.tables[x]}, {p: self.tables[p] for p in parents})

    def __str__(self):
        if self.tables is None:
            return ""

        if self.given is None:
            return "P(" + ", ".join(list(self.tables.keys())) + ")"
        return "P(" + ", ".join(self.tables.keys()) + " | " + ", ".join(self.given.keys()) + ")"


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

        # print(self.incoming)

    def __call__(self, v: set):
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
def C(G: LatentGraph):
    return G.all_c_components()


class Symbol:

    def __init__(self, s, exp, symbol):
        self.symbol = symbol
        self.s = s
        self.exp = exp

    def __str__(self):

        rep = ""
        if self.s is not None and len(self.s) > 0:
            s = self.s
            if isinstance(s, set):
                s = list(s)
            for i in range(len(s)):
                if not isinstance(i, str):
                    s[i] = "[" + ", ".join(list(s[i])) + "]"

            rep += self.symbol + "_[" + ", ".join(self.s) + "] "

        if isinstance(self.exp, list):
            if len(self.exp) > 1:
                rep += "["
            for item in self.exp:
                if isinstance(item, Symbol) or isinstance(item, ProbabilityDistribution):
                    rep += str(item) + (", " if len(self.exp) > 1 else "")
                else:
                    print("CONFUSED: ", type(item))
            if len(self.exp) > 1:
                rep += "]"
        else:
            rep += str(self.exp)

        return rep


class SigmaObj(Symbol):

    def __init__(self, s, exp):
        super().__init__(s, exp, "Sigma")


class PiObj(Symbol):

    def __init__(self, s, exp):
        super().__init__(s, exp, "Pi")


# noinspection PyPep8Naming
def Sigma(s, X):
    return SigmaObj(s, X)


# noinspection PyPep8Naming
def Pi(s, X):
    return PiObj(s, X)


# noinspection PyPep8Naming
def ID(y: set, x: set, P: ProbabilityDistribution, G: LatentGraph, rec=0):

    print("*" * 10, rec, "*" * 10)
    print("y", str(y), "x", str(x))

    # noinspection PyPep8Naming
    def An(X: set):
        return set().union(*[G.ancestors(v) for v in X]) | X

    def children(v):
        return G.children(v)

    def parents(v):
        print(v, G.parents(v))
        return G.parents(v)

    V = G.v

    # ID

    # 1 - if X == {}, return Sigma_{v\y}P(v)
    if x == set():
        print("1", str(y), str(x), V)
        return Sigma(V - y, [P(v) for v in y])

    # 2 - if V != An(Y)_G
    if V != An(y):          # print("2", str(y), str(x))
        # return ID(y, x ∩ An(Y)_G, P(An(Y)), An(Y)_G)
        print("2")
        return ID(y, x & An(y), P(An(y)), G(An(y)), rec+1)

    # 3 - let W = (V\X) \ An(Y)_{G_X}.
    G.disable_incoming(*x)
    W = (V - x) - An(y)
    G.reset_disabled()

    print("W:", str(W))

    # if W != {}
    if W != set():          # print("3", str(y), str(x))
        # return ID(y, x ∪ w, P, G)
        return ID(y, x | W, P, G, rec+1)

    # 4 - if C(G\X) == { S_1, ..., S_k},
    if len(S := C(G(V - x))) > 1:       # print("4", str(y), str(x))
        # return Sigma_{v\(y ∪ x)} Gamma_i id_algorithm(s_i, v \ s_i, P, G)
        return Sigma(V - (y | x), Pi(S, [ID(s, V - s, P, G, rec+1) for s in S]))

    #   if C(G \ X) == {S},
    if len(C(G(V - x))) == 1:

        S = S[0]  # Temp; S is currently a list of one element

        #   5 - if C(G) == {G}
        if C(G) == G:           # print("5", str(y), str(x))
            # throw FAIL(G, S)
            raise FAIL(G, C(G))

        #   6 - if S ∈ C(G)
        if S in C(G):

            print("6", str(y), str(x))
            # return Sigma_{S\Y} Gamma_{V_i ∈ S} P(v_i | v_P{pi}^{i -1})
            print("Parents:", parents(list(S)[0]))
            return Sigma(S-y, Pi(S, [P(Vi, parents(Vi)) for Vi in S]))

        #   7 -  if (∃S')S ⊂ S' ∈ C(G)
        #       return ID(y, x ∩ S', Gamma_{V_i ∈ S'} P(V_i | V_{pi}^{i-1} ∩ S', v_{pi}^{i-1} \ S'), S')

    print("end of line")
    raise FAIL(G, C(G))
