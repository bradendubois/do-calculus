from itertools import product
from typing import List, Iterable, Set, Tuple

from ..core.Graph import Graph

# A method to convert a Graph and a set of unobservable variables into a LatentGraph,
#   in which all unobservable variables are replaced with bidirected arcs


class LatentGraph(Graph):

    def __init__(self, g: Graph, u: Set[str]):
        super().__init__(g.v, g.e, topology=g.topology_sort())

        V = g.v.copy()
        E = set(g.e.copy())
        
        Un = u.copy()

        # Collapse unobservable variables, such as U1 -> U2 -> V ==> U1 -> V
        reduction = True
        while reduction:
            reduction = False

            remove = set()
            for u in Un:

                parents = [edge[0] for edge in E if edge[1] == u]       # Edges : parent -> u
                children = [edge[1] for edge in E if edge[0] == u]      # Edges : u -> child

                # All parents are unobservable, all children are observable, at least one parent
                if all(x in u for x in parents) and len(parents) > 0 and all(x not in u for x in children):
                    reduction = True

                    # Remove edges from parents to u
                    for parent in parents:
                        E.remove((parent, u))

                    # Remove edges from u to children
                    for child in children:
                        E.remove((u, child))

                    # Replace with edge from edge parent to each child
                    for cr in product(parents, children):
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

        super().__init__(V, E, [x for x in g.topology_sort() if x in V - u])


# TODO Merge this into the above LatentGraph
class Graph:

    def __init__(self, edges: Set[Tuple[str, str, str]], vertices: Set[str], fixed_topology: List[str] = None):

        self.Edges = edges
        self.V = vertices                   # for this member and the next we use the notation in Shpitser's alg
        self.C = set()                      # this is components
        self.bdV = set()                    # bidirected vertices connected to bidrected edges
        self.AdjList = dict()
        self.bdAdjList = dict()
        self.Parents = dict()
        self.Children = dict()
        self.bdEdges = set()
        self.bdV = self.V.copy()

        for v in self.V:
            self.AdjList[v] = set()
            self.bdAdjList[v] = set()
            self.Parents[v] = set()
            self.Children[v] = set()

        for (ex, ey, direction) in self.Edges:

            if direction == "->":
                self.AdjList[ex].add(ey)
                self.AdjList[ey].add(ex)
                self.Children[ex].add(ey)
                self.Parents[ey].add(ex)

            else:
                self.bdEdges.add((ex, ey))
                self.bdAdjList[ex].add(ey)
                self.bdAdjList[ey].add(ex)
                self.bdV.update({ex, ey})

        self.C = self.make_components()

        # Allows passing a topology down to a subgraph
        if fixed_topology:

            # filter any vertices from the given topology that don't exist as vertices in the graph
            filtered_topology = [x for x in fixed_topology if x in vertices]

            # ensure topology fully represents the graph
            assert all(x in vertices for x in filtered_topology), "vertex in the given topology is not in the graph!"
            assert all(x in filtered_topology for x in vertices), "vertex in the graph is not in the given topology!"

            self.v_Pi = filtered_topology

        # Otherwise, generate it
        else:
            self.v_Pi = []
            self.kahns()

    def __str__(self):
        return f"Graph: V = {', '.join(self.V)}, E = {', '.join(list(map(str, self.Edges)))}"

    def __getitem__(self, v: Set[str]):
        e = {(s, t, direction) for (s, t, direction) in self.Edges if s in v and t in v}
        return Graph(e, self.V & v, self.v_Pi)

    def __eq__(self, other):
        if not isinstance(other, Graph):
            return False

        # Need to check Edges more carefully; for bi-directed edges, the order of the vertices does not matter.
        return self.V == other.V and self.bdV == other.bdV and \
               all((e[0], e[1]) in other.bdEdges or (e[1], e[0]) in other.bdEdges for e in self.bdEdges) and \
               all((e[0], e[1]) in self.bdEdges or (e[1], e[0]) in self.bdEdges for e in other.bdEdges) and \
               all((e[0], e[1], e[2]) in other.Edges or (e[1], e[0], e[2]) in other.Edges for e in self.Edges) and \
               all((e[0], e[1], e[2]) in self.Edges or (e[1], e[0], e[2]) in self.Edges for e in other.Edges)

    # puts nodes in topological ordering
    def kahns(self):

        edges = self.Edges.copy()
        vertices = self.V.copy()

        s = vertices - ({e[0] for e in edges if e[2] == '->'} | {e[1] for e in edges if e[2] == '->'})
        s |= set([e[0] for e in edges if e[2] == '->' and e[0] not in {g[1] for g in edges if g[2] == '->'}])
        s = list(s)

        while s:
            n = s.pop()
            self.v_Pi.append(n)

            ms = {e[1] for e in edges if e[0] == n and e[2] == '->'}
            for m in ms:
                edges.remove((n, m, '->'))
                if {e for e in edges if e[1] == m and e[2] == '->'} == set():
                    s.append(m)

    def make_components(self):

        ans = []
        all_v = self.bdV.copy()
        visited = set()

        while all_v:
            start = all_v.pop()
            component = []
            q = [start]

            while q:
                v = q.pop(0)
                if v not in visited:
                    visited.add(v)
                    component.append(v)
                    q.extend({vs for vs in self.bdAdjList[v] if vs not in visited})

            if component:
                ans.append(set(component))

        return ans

    def ancestors(self, y: Set[str]):
        ans = y.copy()
        for v in y:
            for p in self.Parents[v]:
                ans |= self.ancestors({p})
        return ans

    def without_incoming(self, x: Iterable[str]):
        return Graph(self.Edges - {edge for edge in self.Edges if edge[1] in x and edge[2] == '->'}, self.V.copy())

    def collider(self, v1, v2, v3):
        return (v1, v2, '->') in self.Edges and (v3, v2, '->') in self.Edges

    def all_paths(self, x: Iterable[str], y: Iterable[str]):

        def path_list(s, t):  # returns all paths from X to Y regardless of direction of link (no bd links)

            from_s_s = [[s]]
            ans = []
            while from_s_s:
                from_s = from_s_s.pop(0)

                # Directed links
                for each in self.AdjList[from_s[-1]]:
                    if each == t:
                        path = from_s.copy()
                        path.append(t)
                        ans.append(path)
                    elif each not in from_s:
                        r = from_s.copy()
                        r.append(each)
                        from_s_s.append(r)

                # Bidirected links
                for each in self.bdAdjList[from_s[-1]]:
                    if each == t:
                        path = from_s.copy()
                        path.append("U")
                        path.append(t)
                        ans.append(path)
                    elif each not in from_s:
                        r = from_s.copy()
                        r.append("U")
                        r.append(each)
                        from_s_s.append(r)
            return ans

        return [path_list(q, w) for q, w in product(x, y)]

    def ci(self, x: Set[str], y: Set[str], z: Set[str]):
        paths = self.all_paths(x, y)
        for path_pair in paths:
            for path in path_pair:
                broke = False
                for idx, element in enumerate(path):
                    if 0 < idx < len(path) - 1:
                        if self.collider(path[idx - 1], element, path[idx + 1]):
                            return False
                    if element in z:
                        broke = True
                        break
                if not broke:
                    return False
        return True
