#########################################################
#                                                       #
#   Graph                                               #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# This will serve as a way to break up the behemoth Causal Graph into smaller sections.
#   We can isolate more generalized graph code here, as well as create a better way to "erase" incoming or outgoing
#   edges, but only temporarily; this will improve "reach", "parents", etc.

from probability_structures.VariableStructures import *

# These functions should work with any sort of Variable type, or the name itself
CG_Types = str or Variable or Outcome or Intervention


class Graph:

    """A basic graph, with edge control."""

    def __init__(self, v: set, e: set):
        """
        Initializer for a basic Graph.
        :param v: A set of vertices
        :param e: A set of edges, each edge being (source, target)
        """

        self.v = v
        self.e = e

        # Declare the keys (which are vertices)
        self.incoming = {vertex.strip(): set() for vertex in v}
        self.outgoing = {vertex.strip(): set() for vertex in v}

        for edge in e:
            self.outgoing[edge[0].strip()].add(edge[1].strip())
            self.incoming[edge[1].strip()].add(edge[0].strip())

        self.outgoing_disabled = set()
        self.incoming_disabled = set()

        self.topology_map = {vertex: 0 for vertex in v}

        def initialize_topology(v: CG_Types, depth=0):
            """
            Helper function to initialize the ordering of the Variables in the graph
            :param v: A Variable to set the ordering of, and then all its children
            :param depth: How many "levels deep"/variables traversed to reach current
            """
            label = to_label(v)
            self.topology_map[label] = max(self.topology_map[label], depth)
            for child in [c for c in self.outgoing[label]]:
                initialize_topology(child, depth+1)

        # Begin the topological ordering, which is started from every "root" in the graph
        for r in [root_node for root_node in v if len(self.incoming[root_node]) == 0]:
            initialize_topology(r)

    def parents(self, v: CG_Types) -> set:
        """
        Get the parents of v, which may actually be currently controlled
        :param v: A variable in our graph
        :return: All parents reachable (which would be none if being controlled)
        """
        label = to_label(v)
        if label in self.incoming_disabled:
            return set()

        return {p for p in self.incoming[label] if label not in self.outgoing_disabled}

    def children(self, v: CG_Types) -> set:
        """
        Get the children of v, which may actually be currently controlled
        :param v: A variable in our graph
        :return: All children reachable (which would be none if being controlled)
        """
        label = to_label(v)
        if label in self.outgoing_disabled:
            return set()

        return {c for c in self.outgoing[label] if label not in self.incoming_disabled}

    def full_ancestors(self, v: CG_Types) -> set:
        """
        Get the ancestors of v, accounting for disabled vertices
        :param v: The vertex to find all ancestors of
        :return: A set of reachable ancestors of v
        """

        ancestors = set()
        queue = []
        queue.extend(self.parents(v))

        while queue:
            current = queue.pop(0)
            ancestors.add(current)
            queue.extend(self.parents(current))

        return ancestors

    def full_reach(self, v: CG_Types) -> set:
        """
        Get the reach of v, accounting for disabled vertices
        :param v: The vertex to find all descendants of
        :return: A set of reachable descendants of v
        """

        children = set()
        queue = []
        queue.extend(list(self.children(v)))

        while queue:
            current = queue.pop(0)
            children.add(current)
            queue.extend(list(self.children(current)))

        return set(children)

    def disable_outgoing(self, *disable: CG_Types):
        """
        Disable the given vertices' outgoing edges
        :param disable: Any number of vertices to disable
        """
        for v in disable:
            self.outgoing_disabled.add(to_label(v))

    def disable_incoming(self, *disable: CG_Types):
        """
        Disable the given vertices' incoming edges
        :param disable: Any number of vertices to disable
        """
        for v in disable:
            self.incoming_disabled.add(to_label(v))

    def reset_disabled(self):
        """
        Clear and reset all the disabled edges, restoring the graph
        """
        self.outgoing_disabled.clear()
        self.incoming_disabled.clear()

    def get_topology(self, v: CG_Types) -> int:
        """
        Determine the "depth" a given Variable is at in a topological sort of the graph
        :param v: The variable to determine the depth of
        :return: Some non-negative integer representing the depth of this variable
        """
        return self.topology_map[to_label(v)]


def to_label(item: str or Variable or Outcome or Intervention) -> str:
    """
    Convert a variable to its string name, if not already provided as such
    :param item: The item to convert, either a string (done) or some Variable
    :return: A string name of the given item, if not already provided as a string
    """
    return item if isinstance(item, str) else item.name
