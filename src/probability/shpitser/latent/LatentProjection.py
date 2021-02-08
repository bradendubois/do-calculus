#########################################################
#                                                       #
#   LatentProjection                                    #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

import itertools

from src.probability.structures.Graph import Graph
from src.probability.shpitser.structures.LatentGraph import LatentGraph

# A method to convert a Graph and a set of unobservable variables into a LatentGraph,
#   in which all unobservable variables are replaced with bidirected arcs


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
