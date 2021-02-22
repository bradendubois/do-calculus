#########################################################
#                                                       #
#   LatentGraph                                         #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

from src.probability.structures.Graph import Graph

# A representation of a Latent Graph, in which we have replaced all unobservable
#   variables with bidirected arcs between the observable variables


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
