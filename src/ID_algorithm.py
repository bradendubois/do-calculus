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

from probability_structures.Graph import Graph
from probability_structures.CausalGraph import CausalGraph
from probability_structures.VariableStructures import Variable

# y : some variable or set of variables
# x : some variable or set of variables (interventions) ?
# P : some probability distribution, likely representable as the tables of a CG
# G : causal diagram having undergone latent projection
from util.parsers.GraphLoader import parse_graph_file_data

# Load the graph
eelworm_cg = CausalGraph(**parse_graph_file_data("./graphs/full/fumigants_eelworms.json"))


# Some boilerplate test that'll allow me to layout ID very cleanly. Maybe. Hopefully!
class ProbabilityDistribution:

    def __init__(self):
        pass

    def ancestors(self, *args):
        return self

    def p(self, *args):
        return 0


class ExtendedGraph(Graph):
    
    def __init__(self, v, e, u):
        super().__init__(v, e)
        self.u = u - (v - u)

    def subgraph(self, v):
        v_p = {vertex for vertex in self.v if vertex in v}
        e_p = {edge for edge in self.e if edge[0] in v and edge[1] in v}
        return ExtendedGraph(v_p, e_p, set())

    def latent_projection(self):

        v = self.v.copy()
        e = set(self.e.copy())
        uc = self.u.copy()

        # Collapse some unobservable variables, such as U1 -> U2 -> V ==> U1 -> V
        reduction = True
        while reduction:

            reduction = False
            remove = set()
            for u in uc:

                parents = [edge[0] for edge in e if edge[1] == u]
                children = [edge[1] for edge in e if edge[0] == u]

                if all(x in self.u for x in parents) and len(parents) > 0 and all(x not in self.u for x in children):
                    reduction = True

                    for parent in parents:
                        e.remove((parent, u))

                    for child in children:
                        e.remove((u, child))

                    for cr in itertools.product(parents, children):
                        e.add((cr[0], cr[1]))

                    remove.add(u)

            for r in remove:
                v.remove(r)
                uc.remove(r)

        # Convert all remaining unobservable to a list to iterate through
        uc = list(uc)
        while len(uc) > 0:

            # Take one "current" unobservable to remove, and remove it from the graph entirely
            cur = uc.pop()
            v.remove(cur)

            try:
                assert len([edge for edge in e if edge[1] == cur]) == 0, \
                    "Unobservable still had parent left. I don't think it should."
            except AssertionError:
                print(cur, "still had parent")
                print(e)

            child_edges = {edge for edge in e if edge[0] == cur}
            e -= child_edges

            child_edges = list(child_edges)
            for i in range(len(child_edges)):
                a, b = child_edges[i], child_edges[(i + 1) % len(child_edges)]
                e.add((a[1], b[1]))
                e.add((b[1], a[1]))

            # Old Implementation, adds excessive amount of edges (C-components become 'dense' sub-graphs)
            # children = set(x[1] for x in child_edges if x[1] != cur)
            # for cross in itertools.product(children, children):
            #     c1, c2 = cross
            #     if c1 == c2:
            #         continue

            #     e.add((c1, c2))
            #     e.add((c2, c1))

        print(v)
        print(e)
        return ExtendedGraph(v, e, set())


class LatentGraph(Graph):

    def __init__(self, v, e):
        super().__init__(v, e)

    def bidirected(self, s, t):
        return (s, t) in self.e and (t, s) in self.e

    def c_component(self, v):
        component = set()       # C Component is a set of vertices, can construct a subgraph
        seen = set()            # Prevent infinite loops, just a set of vertices examined

        component.add(v)        # C component is at least a component of 1, the original vertex
        queue = list(self.incoming[v] | self.outgoing[v])       # Start with everything connected to v

        while len(queue) > 0:

            current = queue.pop()
            if current not in seen:
                seen.add(current)

                # Can add anything that is connected by a bidirected arc
                if any(self.bidirected(item, current) for item in component):
                    component.add(current)
                    queue = list(self.incoming[current] | self.outgoing[current])

        return component


# noinspection PyPep8Naming
def id_algorithm(y: set, x: set, P: ProbabilityDistribution, G: ExtendedGraph):

    # 1 - if X == {}, return Sigma_{v\y}P(v)
    if len(x) == 0:
        return sum([P.p(v) for v in G.v - y])

    # 2 - if V != An(Y)_G
    #   return ID(y, x ∩ An(Y)_G, P(An(Y)), An(Y)_G)
    if G.v != G.ancestors(y):
        return id_algorithm(y, x & G.ancestors(y), P.ancestors(y), G.subgraph(G.ancestors(y)))

    # 3 - let W = (V\X) \ An(Y)_{G_X}.
    # if W != {}, return id_algorithm(y, x ∪ w, P, G)
    # if G.v - x != set():
    #     return id_algorithm(y, x | )

    # 4 - if C(G\X) == { S_1, ..., S_k},
    #   return Sigma_{v\(y ∪ x)} Gamma_i id_algorithm(s_i, v \ s_i, P, G)

    #   if C(G \ X) == {S},
    #   5 - if C(G) == {G}, throw FAIL(G, S)
    #   6 - if S ∈ C(G), return Sigma_{S\Y} Gamma_{V_i ∈ S} P(v_i | v_P{pi}^{i -1})
    #   7 -  if (∃S')S ⊂ S' ∈ C(G)
    #       return ID(y, x ∩ S', Gamma_{V_i ∈ S'} P(V_i | V_{pi}^{i-1} ∩ S', v_{pi}^{i-1} \ S'), S')

    return
