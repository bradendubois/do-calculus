from typing import Collection, Optional, Sequence, Set, Tuple, Union

from .Types import VClass, Vertex


class Graph:

    """A basic graph, with edge control."""

    def __init__(self, v: Set[str], e: Set[Tuple[str, str]], topology: Optional[Sequence[Union[str, VClass]]] = None):
        """
        Initializer for a basic Graph.
        @param v: A set of vertices
        @param e: A set of edges, each edge being (source, target)
        @param topology: An optional sequence of vertices defining the topological ordering of the graph
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

        if not topology:
            topology = self.topology_sort()
        else:
            topology = list(filter(lambda x: x in v, topology))

        self.topology_map = {vertex: index for index, vertex in enumerate(topology, start=1)}

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

    def parents(self, v: Vertex) -> Collection[Vertex]:
        """
        Get the parents of v, which may actually be currently controlled
        @param v: A variable in our graph
        @return: All parents reachable (which would be none if being controlled)
        """
        label = to_label(v)
        if label in self.incoming_disabled:
            return set()

        return {p for p in self.incoming[label] if p not in self.outgoing_disabled and p not in self.outgoing[label]}

    def children(self, v: Vertex) -> Collection[Vertex]:
        """
        Get the children of v, which may actually be currently controlled
        @param v: A variable in our graph
        @return: All children reachable (which would be none if being controlled)
        """
        label = to_label(v)
        if label in self.outgoing_disabled:
            return set()

        return {c for c in self.outgoing[label] if c not in self.incoming_disabled and c not in self.incoming[label]}

    def ancestors(self, v: Vertex) -> Collection[Vertex]:
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

    def descendants(self, v: Vertex) -> Collection[Vertex]:
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

        return children

    def disable_outgoing(self, *disable: Vertex):
        """
        Disable the given vertices' outgoing edges
        @param disable: Any number of vertices to disable
        """
        for v in disable:
            self.outgoing_disabled.add(to_label(v))

    def disable_incoming(self, *disable: Vertex):
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

    def get_topology(self, v: Vertex) -> int:
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

    def descendant_first_sort(self, variables: Collection[Vertex]) -> Sequence[Vertex]:
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

    def without_incoming_edges(self, x: Collection[Vertex]):

        v = self.v.copy()
        e = {(s, t) for (s, t) in self.e if t not in x}

        return Graph(v, e)

    def without_outgoing_edges(self, x: Collection[Vertex]):

        v = self.v.copy()
        e = {(s, t) for (s, t) in self.e if s not in x}

        return Graph(v, e)


def to_label(item: VClass) -> str:
    """
    Convert a variable to its string name, if not already provided as such
    @param item: The item to convert, either a string (done) or some Variable
    @return: A string name of the given item, if not already provided as a string
    """
    return item.strip("'") if isinstance(item, str) else item.name.strip("'")
