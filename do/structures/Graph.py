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

from typing import Collection, Sequence, Set, Tuple, Union

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

        topology = self.topology_sort()
        self.topology_map = {vertex: topology.index(vertex) for vertex in v}

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

    def sinks(self) -> Collection[str]:
        """
        Get the sinks of the graph G.
        @return: A collection of string vertices in G that have no descendants.
        """
        return set([x for x in self.v if len(self.children(x)) == 0])

    def parents(self, v: Union[V_Type, str]) -> Collection[Union[str, V_Type]]:
        """
        Get the parents of v, which may actually be currently controlled
        @param v: A variable in our graph
        @return: All parents reachable (which would be none if being controlled)
        """
        label = to_label(v)
        if label in self.incoming_disabled:
            return set()

        return {p for p in self.incoming[label] if p not in self.outgoing_disabled and p not in self.outgoing[label]}

    def children(self, v: Union[V_Type, str]) -> Collection[Union[str, V_Type]]:
        """
        Get the children of v, which may actually be currently controlled
        @param v: A variable in our graph
        @return: All children reachable (which would be none if being controlled)
        """
        label = to_label(v)
        if label in self.outgoing_disabled:
            return set()

        return {c for c in self.outgoing[label] if c not in self.incoming_disabled and c not in self.incoming[label]}

    def ancestors(self, v: Union[V_Type, str]) -> Collection[Union[str, V_Type]]:
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

    def descendants(self, v: Union[V_Type, str]) -> Collection[Union[str, V_Type]]:
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

    def disable_outgoing(self, *disable: Union[V_Type, str]):
        """
        Disable the given vertices' outgoing edges
        @param disable: Any number of vertices to disable
        """
        for v in disable:
            self.outgoing_disabled.add(to_label(v))

    def disable_incoming(self, *disable: Union[V_Type, str]):
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

    def get_topology(self, v: Union[V_Type, str]) -> int:
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

    def __getitem__(self, v: set):
        """
        Compute a subset V of some Graph G.
        :param v: A set of variables in G.
        :return: A Graph representing the subgraph G[V].
        """
        return Graph({s for s in self.v if s in v}, {s for s in self.e if s[0] in v and s[1] in v})

    def descendant_first_sort(self, variables: Collection[Union[str, V_Type]]) -> Sequence[Union[str, V_Type]]:
        """
        A helper function to "sort" a list of Variables/Outcomes/Interventions such that no element has a
        "parent"/"ancestor" to its left
        @param variables: A list of any number of Variable/Outcome/Intervention instances
        @return: A sorted list, such that any instance has no ancestor earlier in the list
        """
        return sorted(variables, key=lambda v: self.get_topology(v))

    def topology_sort(self) -> Sequence[str]:

        topology = []
        v = self.v.copy()
        e = self.e.copy()

        while len(v) > 0:

            roots = set(filter(lambda t: not any((s, t) in e for s in v), v))
            assert len(roots) > 0

            topology.extend(sorted(list(roots)))
            v -= roots
            e -= set(filter(lambda edge: edge[0] in roots, e))

        return topology

    # noinspection PyPep8Naming
    def V(self, i) -> Sequence[str]:
        """
        Return all vertices in the graph up to some given value (exclusive) in a topological ordering.
        @param i: Some integer in the range [1, |V|]
        @return: A sequence of vertices V1, V2, ..., Vi-1 in the graph.
        """
        assert 1 <= i <= len(self.v), "Invalid integer i; not in the range [1, |V|]"
        return self.topology_sort()[:i]


def to_label(item: V_Type) -> str:
    """
    Convert a variable to its string name, if not already provided as such
    @param item: The item to convert, either a string (done) or some Variable
    @return: A string name of the given item, if not already provided as a string
    """
    return item.strip("'") if isinstance(item, str) else item.name.strip("'")
