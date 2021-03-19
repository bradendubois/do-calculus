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

from typing import Collection, Set, Tuple, Union

from .Types import V_Type


class Graph:

    """A basic graph, with edge control."""

    def __init__(self, v: Set[str], e: Set[Tuple[str, str]]):
        """
        Initializer for a basic Graph.
        @param v: A set of vertices
        @param e: A set of edges, each edge being (source, target)
        """

        self.v = v
        self.e = {(s.strip(), t.strip()) for s, t in e}

        # Declare the keys (which are vertices)
        self.incoming = {vertex.strip(): set() for vertex in v}
        self.outgoing = {vertex.strip(): set() for vertex in v}

        for s, t in e:
            self.outgoing[s].add(t)
            self.incoming[t].add(s)

        self.outgoing_disabled = set()
        self.incoming_disabled = set()

        self.topology_map = {vertex: 0 for vertex in v}

        def initialize_topology(vertex: V_Type, depth=0):
            """
            Helper function to initialize the ordering of the Variables in the graph
            @param vertex: A Variable to set the ordering of, and then all its children
            @param depth: How many "levels deep"/variables traversed to reach current
            """
            label = to_label(vertex)
            self.topology_map[label] = max(self.topology_map[label], depth)
            for child in [c for c in self.outgoing[label] if c not in self.incoming[label]]:
                initialize_topology(child, depth+1)

        # Begin the topological ordering, which is started from every "root" in the graph
        for r in [root_node for root_node in v if len(self.incoming[root_node]) == 0]:
            initialize_topology(r)

    def __str__(self) -> str:
        """
        String builtin for the Graph class
        @return: A string representation of the given Graph instance
        """
        msg = "Vertices: " + ", ".join(sorted(i for i in self.v)) + "\n"
        msg += "Edges:\n" + "\n".join(" -> ".join(i for i in edge) for edge in self.e)
        return msg

    def roots(self) -> Collection[str]:
        """
        Get the roots of the the graph G.
        @return: A set of vertices (strings) in G that have no parents.
        """
        return set([x for x in self.v if len(self.parents(x)) == 0])

    def parents(self, v: V_Type) -> Collection[Union[str, V_Type]]:
        """
        Get the parents of v, which may actually be currently controlled
        @param v: A variable in our graph
        @return: All parents reachable (which would be none if being controlled)
        """
        label = to_label(v)
        if label in self.incoming_disabled:
            return set()

        return {p for p in self.incoming[label] if p not in self.outgoing_disabled and p not in self.outgoing[label]}

    def children(self, v: V_Type) -> Collection[Union[str, V_Type]]:
        """
        Get the children of v, which may actually be currently controlled
        @param v: A variable in our graph
        @return: All children reachable (which would be none if being controlled)
        """
        label = to_label(v)
        if label in self.outgoing_disabled:
            return set()

        return {c for c in self.outgoing[label] if c not in self.incoming_disabled and c not in self.incoming[label]}

    def ancestors(self, v: V_Type) -> Collection[Union[str, V_Type]]:
        """
        Get the ancestors of v, accounting for disabled vertices
        @param v: The vertex to find all ancestors of
        @return: A set of reachable ancestors of v
        """

        ancestors = set()
        queue = []
        queue.extend(self.parents(v))

        while queue:
            current = queue.pop(0)
            ancestors.add(current)
            queue.extend(self.parents(current))

        return ancestors

    def reach(self, v: V_Type) -> Collection[Union[str, V_Type]]:
        """
        Get the reach of v, accounting for disabled vertices
        @param v: The vertex to find all descendants of
        @return: A set of reachable descendants of v
        """

        children = set()
        queue = []
        queue.extend(list(self.children(v)))

        while queue:
            current = queue.pop(0)
            children.add(current)
            queue.extend(list(self.children(current)))

        return set(children)

    def disable_outgoing(self, *disable: V_Type):
        """
        Disable the given vertices' outgoing edges
        @param disable: Any number of vertices to disable
        """
        for v in disable:
            self.outgoing_disabled.add(to_label(v))

    def disable_incoming(self, *disable: V_Type):
        """
        Disable the given vertices' incoming edges
        @param disable: Any number of vertices to disable
        """
        for v in disable:
            self.incoming_disabled.add(to_label(v))

    def reset_disabled(self):
        """
        Clear and reset all the disabled edges, restoring the graph
        """
        self.outgoing_disabled.clear()
        self.incoming_disabled.clear()

    def get_topology(self, v: V_Type) -> int:
        """
        Determine the "depth" a given Variable is at in a topological sort of the graph
        @param v: The variable to determine the depth of
        @return: Some non-negative integer representing the depth of this variable
        """
        return self.topology_map[to_label(v)]

    def copy(self):
        """
        Public copy method; copies v, e, and the disabled sets
        @return: A copied Graph
        """
        return self.__copy__()

    def __copy__(self):
        """
        Copy builtin allowing the Graph to be copied
        @return: A copied Graph
        """
        copied = Graph(self.v.copy(), set(self.e.copy()))
        copied.incoming_disabled = self.incoming_disabled.copy()
        copied.outgoing_disabled = self.outgoing_disabled.copy()
        return copied

    def topological_variable_sort(self, variables: Collection[Union[str, V_Type]]) -> Collection[Union[str, V_Type]]:
        """
        A helper function to abstract what it means to "sort" a list of Variables/Outcomes/Interventions
        @param variables: A list of any number of Variable/Outcome/Intervention instances
        @return: A list, sorted (currently in the form of a topological sort)
        """
        if len(variables) == 0:
            return []

        largest_topology = max(self.get_topology(v) for v in variables)
        sorted_variables = [[v for v in variables if self.get_topology(v) == i] for i in range(largest_topology+1)]
        return [item for topology_sublist in sorted_variables for item in topology_sublist]

    def descendant_first_sort(self, variables: Collection[Union[str, V_Type]]) -> Collection[Union[str, V_Type]]:
        """
        A helper function to "sort" a list of Variables/Outcomes/Interventions such that no element has a
        "parent"/"ancestor" to its left
        @param variables: A list of any number of Variable/Outcome/Intervention instances
        @return: A sorted list, such that any instance has no ancestor earlier in the list
        """
        # We can already do top-down sorting, just reverse the answer
        return self.topological_variable_sort(variables)[::-1]


def to_label(item: V_Type) -> str:
    """
    Convert a variable to its string name, if not already provided as such
    @param item: The item to convert, either a string (done) or some Variable
    @return: A string name of the given item, if not already provided as a string
    """
    return item.strip("'") if isinstance(item, str) else item.name.strip("'")
