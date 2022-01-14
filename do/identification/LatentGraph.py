from itertools import product
from typing import List, Iterable, Set, Tuple

from ..core.Graph import Graph


class LatentGraph(Graph):

    def __init__(self, vertices: Set[str], edges: Set[Tuple[str, str]], e_bidirected: Set[Tuple[str, str]], fixed_topology: List[str] = None):
        super().__init__(vertices, edges, fixed_topology)
        self.e_bidirected = e_bidirected.copy()
        self.V = vertices
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
            self.v_Pi = self.__kahns()

    def __str__(self):
        return f"Graph: V = {', '.join(self.v)}, E = {', '.join(list(map(str, self.e)))}, E (Bidirected) = {', '.join(list(map(str, self.e_bidirected)))}"

    def __getitem__(self, v: Set[str]):
        e = {(s, t) for (s, t) in self.e if s in v and t in v}
        e_bidirected = {(s, t) for (s, t) in self.e_bidirected if s in v and t in v}
        return LatentGraph(self.v & v, e, e_bidirected, self.v_Pi)

    def __eq__(self, other):
        if not isinstance(other, LatentGraph):
            return False

        return self.v == other.v and self.e == other.e and \
            all([(e[0], e[1]) in other.e_bidirected or (e[1], e[0]) in other.e_bidirected for e in self.e_bidirected]) and \
            all([(e[0], e[1]) in self.e_bidirected or (e[1], e[0]) in self.e_bidirected for e in other.e_bidirected])

    def biadjacent(self, v: str):
        return {e[0] if e[0] != v else e[1] for e in self.e_bidirected if v in e}

    def ancestors(self, y: Set[str]):
        ans = y.copy()
        for v in y:
            for p in self.parents(v):
                ans |= self.ancestors({p})
        return ans

    # puts nodes in topological ordering
    def __kahns(self):

        edges = self.e.copy()
        vertices = self.v.copy()
        v_Pi = []

        s = vertices - ({e[0] for e in edges} | {e[1] for e in edges})
        s |= set([e[0] for e in edges if e[0] not in {g[1] for g in edges}])
        s = list(s)

        while s:
            n = s.pop()
            v_Pi.append(n)

            ms = {e[1] for e in edges if e[0] == n}
            for m in ms:
                edges.remove((n, m))
                if {e for e in edges if e[1] == m} == set():
                    s.append(m)

        return v_Pi

    def make_components(self):

        ans = []
        all_v = self.v.copy()
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
                    q.extend([vs for vs in self.biadjacent(v) if vs not in visited])

            if component:
                ans.append(set(component))

        return ans

    def without_incoming(self, x: Iterable[str]):
        # return Graph(self.Edges - {edge for edge in self.Edges if edge[1] in x and edge[2] == "->"}, self.V)
        return LatentGraph(self.v, self.e - {e for e in self.e if e[1] in x}, self.e_bidirected, self.v_Pi)

    def collider(self, v1, v2, v3):
        return v1 in self.V and v2 in self.V and v3 in self.V and v1 in self.parents(v2) and v3 in self.children(v2)

    def all_paths(self, x: Iterable[str], y: Iterable[str]):

        def path_list(s, t):  # returns all paths from X to Y regardless of direction of link (no bd links)

            # generate a fake variable to represent unobservable variables
            UNOBSERVABLE = "U"
            while UNOBSERVABLE in self.V:
                UNOBSERVABLE += "U"

            from_s_s = [[s]]
            ans = []
            while from_s_s:
                from_s = from_s_s.pop(0)

                # Directed links
                for each in set(self.parents(from_s[-1])) | set(self.children(from_s[-1])):
                    if each == t:
                        path = from_s.copy()
                        path.append(t)
                        ans.append(path)
                    elif each not in from_s:
                        r = from_s.copy()
                        r.append(each)
                        from_s_s.append(r)

                # Bidirected links
                for each in self.biadjacent(from_s[-1]):
                    if each == t:
                        path = from_s.copy()
                        path.append(UNOBSERVABLE)
                        path.append(t)
                        ans.append(path)
                    elif each not in from_s:
                        r = from_s.copy()
                        r.append(UNOBSERVABLE)
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


def latent_transform(g: Graph, u: Set[str]):

    V = g.v.copy()
    E = set(g.e.copy())
    E_Bidirected = set()

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
            E_Bidirected.add((a[1], b[1]))

    return LatentGraph(V, E, E_Bidirected, [x for x in g.topology_sort() if x in V - u])
