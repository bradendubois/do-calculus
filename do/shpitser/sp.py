from itertools import product
from typing import Iterable, List, Set, Tuple, Union, Optional

d = '->'
b = '<->'


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


class PExpr(list):

    def __init__(self, vs, ps: list = None, proof: List[Tuple[int, List[str]]] = None):
        super().__init__(ps if ps else [])
        self.sigma = list(vs)
        self.internal_proof = proof if proof else []

    def __str__(self):
        buf = ""
        if self.sigma:
            buf += "<sum {" + ", ".join(self.sigma) + "} "

        # Put Distributions (or PExprs with empty summations) first
        for el in filter(lambda x: not isinstance(x, PExpr) or isinstance(x, PExpr) and len(x.sigma) == 0, self):
            if isinstance(el, PExpr):
                buf += str(el)
            elif len(el[1]) > 0:
                buf += f"[{el[0]}|{','.join(el[1])}] "
            else:
                buf += f"[{el[0]}] "

        # Put PExprs after
        for el in filter(lambda x: isinstance(x, PExpr) and len(x.sigma) > 0, self):
            buf += str(el)

        if self.sigma:
            buf += '>'
        return buf

    def pexpr_copy(self):
        copied_contents = []
        for item in self:
            if isinstance(item, PExpr):
                copied_contents.append(item.pexpr_copy())
            else:
                copied_contents.append([item[0], item[1].copy()])
        copied_proof = [(i, [s for s in block]) for i, block in self.internal_proof]
        return PExpr(self.sigma.copy(), copied_contents, copied_proof)

    def copy(self):
        result: PExpr = self.pexpr_copy()
        return result

    def proof(self) -> str:
        s = ""
        for j, block in self.internal_proof:
            indent = " " * 3 * j
            for line in block:
                s += indent + line + '\n'
            s += '\n'

        for child in filter(lambda x: isinstance(x, PExpr), self):
            s += child.proof()
        return s

# noinspection PyPep8Naming
def debugPExpr(f, s=0):
    print("  " * s, type(f), f)
    if type(f) == str:
        return
    for item in f:
        debugPExpr(item, s + 1)


def simplify_expression(original: PExpr, g: Graph, debug=False) -> PExpr:

    def _simplify(current):

        cpt_list_copy = list(filter(lambda i: not isinstance(i, PExpr), list(current).copy()))
        for s in [s for s in current if isinstance(s, PExpr)]:
            c = _simplify(s)

            if s.internal_proof:
                offset = original.internal_proof[-1][0] + 2
            else:
                offset = 1

            s.internal_proof.append((offset, c))

        steps = []

        # """
        # Remove unnecessary variables from body
        for expression in cpt_list_copy:

            while True:
                removed_one = False
                x = {expression[0]}
                for variable in expression[1]:
                    y = {variable}
                    z = set(expression[1]) - y
                    if g.ci(x, y, z):
                        msg1 = f"{', '.join(x)} is independent of {', '.join(y)} given {', '.join(z)}, and can be removed."
                        msg2 = f"p operator removed {variable} from body of {expression[0]} | {expression[1]}"
                        if debug:
                            print(msg1)
                            print(msg2)
                        steps.append(msg1)
                        expression[1].remove(variable)
                        removed_one = True

                if not removed_one:
                    break
        # """

        # Remove unnecessary expressions
        # """
        while True:
            bodies = set().union(*[el[1] for el in current if not isinstance(el, PExpr)])
            search = filter(lambda el: el[0] in current.sigma, current)
            remove = list(filter(lambda el: el[0] not in bodies, search))

            if len(remove) == 0:
                break

            for query in remove:
                current.sigma.remove(query[0])
                current.remove(query)
                msg = f"{query[0]} can be removed."
                if debug:
                    print(msg)
                steps.append(msg)
        # """

        while True:
            sumout = [cpt for cpt in current if cpt[0] in current.sigma and not any([cpt[0] in el[1] for el in current])]
            if not sumout:
                break
            for cpt in sumout:
                current.remove(cpt)
                current.sigma.remove(cpt[0])

        if len(steps) > 0:
            tables = ", ".join(f"P({table[0]} | {', '.join(table[1])})" if len(table[1]) > 0 else f"P({table[0]})" for table in cpt_list_copy)
            steps.append(f"After simplification: {tables}")

        """
        removals = True
        while removals:
            removals = False
            for el0 in p:
                if el0[0] in p.sigma:
                    flag = True
                    for el1 in p:
                        if el0[0] in el1[1]:
                            flag = False
                    if flag:     # means we have A|X and ~A|X for some consistent expression X
                        p.sigma.remove(el0[0])
                        p.remove(el0)
                        print("p_operator removed", el0[0], el0)
                        removals = True
        """

        def distribution_position(item: Union[list, PExpr]):
            if isinstance(item, PExpr):
                if len(item.sigma) == 0:
                    return len(g.v_Pi)
                return len(g.v_Pi) + min(0, *list(map(lambda v: g.v_Pi.index(v), item.sigma)))
            else:
                return g.v_Pi.index(item[0])

        # Sort remaining expressions by the topological ordering
        current.sort(key=distribution_position)

        if len(steps) > 0:
            steps.insert(0, "[***** Simplification *****]")

        return steps

    if original.internal_proof:
        depth = original.internal_proof[-1][0] + 1
    else:
        depth = 1

    p = original.pexpr_copy()
    changes = _simplify(p)
    p.internal_proof.append((depth, changes))
    return p


def p_operator(v: Set[str], p: Union[PExpr, list], proof: List[Tuple[int, List[str]]] = None, debug: bool = True):

    sigma = p.sigma if isinstance(p, PExpr) else []
    cpt_list_copy = list(p).copy()
    v_copy = v.copy()

    ans = PExpr(list(v_copy | set(sigma)), cpt_list_copy, proof)
    if debug:
        print("p_operator returns = ", ans, " v_copy = ", v_copy, " sigma = ", sigma)
    return ans


def parse_graph_string(graph_string: str) -> Graph:

    from re import split

    arrows = ["<->", "<-", "->"]

    splits = graph_string.strip().split(".")[:-1]
    print(splits)

    e = set()
    v = set()

    for item in splits:

        # This would be an item like "X." or "X,Y". in which the vertices exist, but don't have any edges.
        if not any(arrow in item for arrow in arrows):
            v.update(item.split(","))

        parse = split(f'({"|".join(arrows)})', item)

        for i in range(1, len(parse), 2):

            # Left and Right are comma-separated lists of values, arrow being the "->" -style arrow joining them.
            left, arrow, right = parse[i-1].split(","), parse[i], parse[i+1].split(",")

            # Add all vertices into V
            v.update(left)
            v.update(right)

            for s, t in product(left, right):

                if arrow == "<-":
                    e.add((t, s, d))

                elif arrow == "->":
                    e.add((s, t, d))

                elif arrow == "<->":
                    e.add((s, t, b))

                else:
                    print("Invalid Arrow Type:", arrow)

    return Graph(e, v)


# noinspection PyPep8Naming
def P(g: Graph) -> PExpr:
    return PExpr([], [[x, list(g.Parents[x])] for x in g.V])


class FAIL(Exception):
    def __init__(self, f, fp, proof):
        super().__init__(f, fp)
        self.proof = proof


# noinspection PyPep8Naming
def ID(y: Set[str], x: Set[str], p: PExpr, g: Graph, debug: bool = True, i=0, passdown_proof: Optional[List[Tuple[int, List[str]]]] = None) -> PExpr:

    def s(a_set):
        if len(a_set) == 0:
            return "Ø"
        return "{" + ', '.join(a_set) + "}"

    # The continuation of a proof that is ongoing if this is a recursive ID call, or a 'fresh' new proof sequence otherwise
    proof_chain = passdown_proof if passdown_proof else []

    # noinspection PyPep8Naming
    def An(vertices):
        return g.ancestors(vertices)

    proof_chain.append((i, [f"ID Begin: Y = {s(y)}, X = {s(x)}"]))

    if debug:
        print(i * " " * 3, "Components", *g.C)

    # 1
    if x == set():
        proof_chain.append((i, [
            "1: if X == Ø, return Σ_{V \\ Y} P(V)",
            f"  --> Σ_{s(g.V - y)} P({s(g.V)})",
            "",
            f"[***** Standard Probability Rules *****]"
        ]))

        return p_operator(g.V - y, p, proof_chain, debug)

    # 2
    if g.V != An(y):
        w = g.V - An(y)
        proof_chain.append((i, [
            "2: if V != An(Y)",
            f"--> {s(g.V)} != {s(An(y))}",
            "  return ID(y, x ∩ An(y), P(An(Y)), An(Y)_G)",
            f"  --> ID({s(y)}, {s(x)} ∩ {s(An(y))}, P({s(An(y))}), An({s(An(y))})_G)",
            "",
            f"  [***** Do-Calculus: Rule 3 *****]",
            "  let W = V \\ An(Y)_G",
            f"      W = {s(g.V)} \\ {s(An(y))}",
            f"      W = {s(w)}",
            f"  G \\ W = An(Y)_G",
            f"  {s(g.V)} \\ {s(w)} = {s(An(y))}",
            "  P_{x,z} (y | w) = P_{x} (y | w) if (Y ⊥⊥ Z | X, W) _G_X,Z(W)",
            f"  let y = y ({s(y)}), x = x ∩ An(Y) ({s(x & An(y))}), z = w ({s(w)})" ", w = Ø",
            "  P_{" f"{s((x & An(y)) | w)}" "} " f"({s(y)}) = P_{s(x & An(y))} ({s(y)}) if ({s(y)} ⊥⊥ {s(w)} | {s(x & An(y))}) _G_{s(x)}",
        ]))

        return ID(y, x & An(y), p_operator(g.V - g[An(y)].V, p, None, debug), g[An(y)], debug, i+1, proof_chain)

    # 3
    w = (g.V - x) - g.without_incoming(x).ancestors(y)

    proof_chain.append((i, [
        "let W = (V \\ X) \\ An(Y)_G_X",
        f"--> W = ({s(g.V)} \\ {s(x)}) \\ An({s(y)})_G_{s(x)}",
        f"--> W = {s(g.V - x)} \\ {s(g.without_incoming(x).ancestors(y))}",
        f"--> W = {s(w)}"
    ]))

    if w != set():
        proof_chain.append((i, [
            "3: W != Ø",
            "  return ID(y, x ∪ w, P, G)",
            f"  --> ID({s(y)}, {s(x)} ∪ {s(w)}, P, G)",
            "",
            "  [***** Do-Calculus: Rule 3 *****]",
            "  P_{x, z} (y | w) = P_{x} if (Y ⊥⊥ Z | X, W)_G_X_Z(W)",
            "  let y = y, x = x, z = w, w = Ø",
            "  P_{x} (y | w) = P_{x,z} (y | w) if (Y ⊥⊥ Z | X, W) _G_X,Z(W)",
            f"  P_{s(x)} ({s(y)}) = P_" "{" f"{s(x)[1:-1]}, {s(w)[1:-1]}" "}" f" ({s(y)}) if ({s(y)} ⊥⊥ {s(w)} | {s(x)})_G_{s(x)}"
        ]))

        return ID(y, x | w, p, g, debug, i+1, proof_chain)

    C_V_minus_X = g[g.V - x].C

    # Line 4
    if len(C_V_minus_X) > 1:
        proof_chain.append((i, [
            "4: C(G \\ X) = {S_1, ..., S_k}",
            f"--> C(G \\ X) = C({s(g.V)} \\ {s(x)}) = {', '.join(list(map(s, C_V_minus_X)))}",
            "  return Σ_{V \\ y ∪ x} Π_i ID(Si, v \\ Si, P, G)",
            "  --> Σ_{" f"{s(g.V)} \\ {s(y)} ∪ {s(x)}" "} Π [",
            *[f"      --> ID({s(Si)}, {s(g.V - Si)}, P, G)" for Si in C_V_minus_X],
            "  ]",
            "",
            "  [***** Proof *****]",
            "  P_{x} (y) = Σ_{v \\ (y ∪ x)} Π_i P_{v \\ S_i} (S_i)",
            "  1. [***** Do-Calculus: Rule 3 *****]",
            "     Π_i P_{v \\ S_i} (S_i) = Π_i P_{A_i} (S_i), where A_i = An(S_i)_G \\ S_i",
            "     Π [",
                *[f"       P_{s(g.V - si)} ({s(si)[1:-1]})" for si in C_V_minus_X],
            "     ] = Π [",
                *[f"       P_{s(g.ancestors(si)-si)} ({s(si)[1:-1]})" for si in C_V_minus_X],
            "     ]",

            "  2. [***** Chain Rule *****]",
            "     Π_i P_{A_i} (S_i) = Π_i Π_{V_j ∈ S_i} P_{A_i} (V_j | V_π^(j-1) \\ A_i)",

            "     Π [",
                *[f"       P_{s(g.ancestors(si)-si)} ({s(si)[1:-1]})" for si in C_V_minus_X],
            "     ] = Π [",
                *[" ".join(["       Π ["]  + [
                    f"P_{s(g.ancestors(si)-si)} ({vj} | {s(set(g.v_Pi[:g.v_Pi.index(vj)]) - g.ancestors({vj}))})" for vj in si
                ] + ["]"]) for si in C_V_minus_X],
            "     ]",

            "  3. [***** Rule 2 or Rule 3 *****]",
            "     Π_i Π_{V_j ∈ S_i} P_{A_i} (V_j | V_π^(j-1) \\ A_i) = Π_i Π_{V_j ∈ S_i} P(V_j | V_π^(j-1))",
            "     a. if A ∈ A_i ∩ V_π^(j-1), A can be removed as an intervention by Rule 2",
            "        All backdoor paths from A_i to V_j with a node not in V_π^(j-1) are d-separated.",
            "        Paths must also be bidirected arcs only.",
            "        let x = x, y = y, z = {A}, w = Ø",
            "        P_{x,z} (y | w) = P_{x} (y | z, w) if (Y ⊥⊥ Z | X, W)_X_Z_",
            "     b. if A ∈ A_i \\ V_π^(j-1), A can be removed as an intervention by Rule 3",
            "         let x = x, y = V_j, z = {A}, w = Ø",
            "         P_{x,z} (y | w) = P_{x} (y | w) if (Y ⊥⊥ Z | X, W)_G_X_Z(W)",
            "         (V_j ⊥⊥ A | V_π^(j-1)) G_{A_i}",

            "     Π [",
                *[" ".join(["       Π ["]  + [
                    f"P_{s(g.ancestors(si)-si)} ({vj} | {s(set(g.v_Pi[:g.v_Pi.index(vj)]) - g.ancestors({vj}))})" for vj in si
                ] + ["]"]) for si in C_V_minus_X],
            "     ] = Π [",
                *[" ".join(["       Π ["]  + [
                    f"P ({vj} | {s(set(g.v_Pi[:g.v_Pi.index(vj)]))})" for vj in si
                ] + ["]"]) for si in C_V_minus_X],
            "     ]",

            "  4. [***** Grouping *****]",
            "     Π_i Π_{V_j ∈ S_i} P(V_j | V_π^(j-1)) = Π_i P(V_i | V_π^(i-1))",

            "     Π [",
                *[" ".join(["       Π ["]  + [
                    f"P ({vj} | {s(set(g.v_Pi[:g.v_Pi.index(vj)]))})" for vj in si
                ] + ["]"]) for si in C_V_minus_X],
            "     ] = Π [",

            "     ]",

            "  5. [***** Chain Rule *****]",
            "     Π_i P(V_i | V_π^(i-1)) = P(v)"
        ]))

        return PExpr(g.V - (y | x), [ID(s_i, g.V - s_i, p, g, debug, i+1) for s_i in C_V_minus_X], proof_chain)

    else:

        # At this point we have a single component
        S = C_V_minus_X[0]

        proof_chain.append((i, [
            "if C(G \\ X) = {S}",
            f"--> C({s(g.V)} \\ {s(x)}) = {s(S)}"
        ]))

        # Line 5
        if set(S) == g.V:
            proof_chain.append((i, [
                "5: if C(G) = {G}: FAIL(G, S)",
                f"--> G, S form hedges F, F' for Px(Y) -> {g}, {S} for P_{x}({y})"
            ]))

            raise FAIL(g, S)

        # Line 6 - a single c-component
        if S in g.C:

            dists = []
            dist_str = []
            for vi in S:
                given = g.v_Pi[:g.v_Pi.index(vi)]
                dist_str.append(f"P({vi})" if len(given) == 0 else f"P({vi} | {', '.join(given)})")
                dists.append([vi, given])

            proof_chain.append((i, [
                f"6: S ∈ C(G)",
                f"--> {s(S)} ∈ {', '.join(list(map(s, g.C)))}",
                "  return Σ_{S-Y} π_{Vi ∈ S} P(Vi | V_π^(i-1))",
                f"  --> Σ_{s(S - y)} π [{', '.join(dist_str)}]",
                "",
                "  [***** Proof *****]",
                f"  G has been partitioned into S = {s(S)} and X = {s(x)} in G = {s(g.V)}.",
                "  There are no bidirected arcs between S and X."
            ]))

            return PExpr(S - y, dists, proof_chain)

        # 7
        else:

            s_prime = next(s for s in g.C if set(s) > set(S))
            p = []

            msg = "  --> P = "

            for v in s_prime:
                rhs0 = g.v_Pi[:g.v_Pi.index(v)]
                rhs1 = rhs0.copy()

                rhs0 = list(set(rhs0) & s_prime)
                rhs1 = list(set(rhs1) - s_prime)
                rhs = rhs0 + rhs1
                p.append([v, rhs])
                msg += f"[{v}{(f' | ' + ', '.join(rhs)) if len(rhs) > 0 else ''}]"

            g_s_prime = g[s_prime]

            proof_chain.append((i, [
                f"7: if ∃(S') S ⊂ S' ∈ C(G)",
                f"--> let S = {s(S)}, S' = {s(s_prime)}",
                f"--> {s(S)} ⊂ {s(s_prime)} ∈ {', '.join(list(map(s, g.C)))}",
                "  return ID(y, x ∩ S', π_{V_i ∈ S'} P(V_i | V_π^(i-1) ∩ S', V_π^(i-1) \\ S'), S')",
                msg,
                f"  --> ID({s(y)}, {s(x)} ∩ {s(s_prime)}, P, G = ({g_s_prime.V}, {g_s_prime.Edges}))",
                "",
                "  [***** Proof *****]",
                f"  G is partitioned into X = {s(x)} and S = {s(S)}, where X ⊂ An(S).",
                "  M_{X \\ S'} induces G \\ (X \\ S') = S'.",
                "  P_{x} = P_{x ∩ S', X \\ S'} = P_{x ∩ S'}.",
            ]))

            return ID(y, x & s_prime, PExpr({}, p), g_s_prime, debug, i+1, proof_chain)


##################################################################################

#########################################
# graph 1
#########################################

g_1 = Graph({('M', 'S', d), ('S', 'C', d), ('M', 'C', d)}, {'C', 'S', 'M'})
g_1_string = "M->S.S,M->C."

g1_q1 = ({'C'}, {'S'})
g1_q2 = ({'C'}, {'M'})
g1_q3 = ({'C'}, {'S', 'M'})

g1_a1 = "C | S = <sum {M} [C|M,S] [M] >"
g1_a2 = "C | M = <sum {S} [C|M,S] [S|M] >"
g1_a3 = "C | S, M = [C|M,S]"

g1_queries = [g1_q1, g1_q2, g1_q3]
g1_answers = [g1_a1, g1_a2, g1_a3]

#########################################
# queries - graph 2
#########################################

g_2 = Graph({('A', 'B', d), ('A', 'C', d), ('B', 'D', d), ('C', 'D', d)}, {'A', 'B', 'C', 'D'})
g_2_string = "A->B,C.B,C->D."

g2_q1 = ({'D'}, {'A'})
g2_q2 = ({'D'}, {'B'})
g2_q3 = ({'D'}, {'C'})
g2_q4 = ({'D'}, {'B', 'C'})

g2_a1 = "D | A = <sum {C, B} [D|A,B,C] [C|A] [B|A] >"
g2_a2 = "D | B = <sum {C, A} [C|A] [A] [D|A,B,C] >"
g2_a3 = "D | C = <sum {A, B} [D|A,B,C] [B|A] [A] >"
g2_a4 = "D | C, B = [D|A,B,C]"

g2_queries = [g2_q1, g2_q2, g2_q3, g2_q4]
g2_answers = [g2_a1, g2_a2, g2_a3, g2_a4]

#########################################
# queries - graph 3
#########################################

g_3 = Graph({('B', 'C', b), ('B', 'D', d), ('C', 'D', d)}, {'B', 'C', 'D'})
g_3_string = "B<->C.B,C->D."

g3_q1 = ({'D'}, {'B'})
g3_q2 = ({'D'}, {'C'})
g3_q3 = ({'D'}, {'B', 'C'})

g3_a1 = "D | B = <sum {C} [C] [D|B,C] >"
g3_a2 = "D | C = <sum {B} [D|B,C] [B] >"
g3_a3 = "D | C, B = [D|B,C]"

g3_queries = [g3_q1, g3_q2, g3_q3]
g3_answers = [g3_a1, g3_a2, g3_a3]

#########################################
# queries - graph 4
#########################################

g_4 = Graph({('S', 'T', d), ('T', 'C', d), ('S', 'C', b)}, {'S', 'T', 'C'})
g_4_string = "S->T->C.S<->C."

g4_q1 = ({'C'}, {'S'})

g4_a1 = "C | S = <sum {T} [T|S] ><sum {S} [C|S,T] [S] >"

g4_queries = [g4_q1]
g4_answers = [g4_a1]

#########################################
# queries - graph 5
#########################################

g_5 = Graph(
    {("X", "Z1", b), ("Z1", "Z3", b),
     ("Z1", "Z2", d), ("X", "Z2", d), ("Z2", "Z3", d), ("X", "Y", d), ("Z2", "Y", d), ("Z3", "Y", d)},
    {"X", "Y", "Z1", "Z2", "Z3"}
)
g_5_string = "X<->Z1<->Z3.X,Z1->Z2->Z3.X,Z2,Z3->Y."

g5_q1 = ({"Y"}, {"X"})      # paper: Sum_{X} [P(Z3 | Z2, Z1, X), P(Z1 | X), P(X)]
g5_q2 = ({"Y"}, {"X", "Z1", "Z2", "Z3"})

g5_a1 = "Y | X = <sum {Z2, Z1, Z3} [Y|X,Z2,Z3] [Z2|X,Z1] ><sum {X} [Z3|Z1,X,Z2] [Z1|X] [X] >"
g5_a2 = "Y | Z2, Z1, X, Z3 = [Y|X,Z2,Z3]"

g5_queries = [g5_q1, g5_q2]
g5_answers = [g5_a1, g5_a2]

#########################################
# queries - graph 6
#########################################

g_6 = Graph(
    {("W1", "W2", b), ("W1", "Y1", b), ("W2", "X", b), ("W1", "X", d), ("X", "Y1", d), ("W2", "Y2", d)},
    {"X", "Y1", "Y2", "W1", "W2"}
)
g_6_string = "Y1<->W1<->W2<->X.W1->X->Y1.W2->Y2."

g6_q1 = ({"Y1", "Y2"}, {"X"})
g6_a1 = "Y2, Y1 | X = <sum {W2} [Y2|W2] > [W2] <sum {W1} [Y1|W1,X] [W1] >"

g6_queries = [g6_q1]
g6_answers = [g6_a1]

#########################################
# queries - graph 7
#########################################

g_7 = Graph(
    {("Z1", "Z2", b), ("Z2", "W", b), ("Z1", "W", b), ("Z2", "X", d), ("X", "W", d), ("W", "Y", d), ("Z1", "Y", d)},
    {"Z1", "Z2", "W", "X", "Y"}
)
g_7_string = "Z1<->Z2<->W<->Z1.Z2->X->W->Y<-Z1."

g7_q1 = ({"Y"}, {"X"})
g7_a1 = "Y | X = <sum {Z1, W} [Y|Z1,Z2,X,W] ><sum {Z2} [W|Z2,Z1,X] [Z2|Z1] [Z1] >"

g7_queries = [g7_q1]
g7_answers = [g7_a1]

#########################################
# queries - graph 8
#########################################

g_8 = Graph({('S1', 'T1', d), ('T1', 'C1', d), ('S1', 'C1', b), ('S2', 'T2', d), ('T2', 'C2', d), ('S2', 'C2', b), ('C2', 'C', d), ('C1', 'C', d)},
            {'S1', 'T1', 'C1', 'S2', 'T2', 'C2', 'C'})
g_8_string = "S1->T1->C1<->S1.S2->T2->C2<->S2.C2->C<-C1."

g8_q1 = ({'C1'}, {'S1'})
g8_q2 = ({'C2'}, {'S2'})
g8_q3 = ({'C1', 'C2'}, {'S1', 'S2'})
g8_q4 = ({'C'}, {'S1', 'S2'})

g8_a1 = "<sum {T1} [T1|S1] <sum {S1} [C1|S1,T1] [S1] >>"
g8_a2 = "<sum {T2} [T2|S2] <sum {S2} [C2|S2,T2] [S2] >>"
g8_a3 = "<sum {T2} [T2|S2] <sum {T1} [T1|S1] ><sum {S1} [C1|S1,T1] [S1] ><sum {S2} [C2|S2,T2] [S2]>>"
g8_a4 = "<sum {C1, C2} [C|C1,C2] <sum {T1} [T1|S1] ><sum {T2} [T2|S2] <sum {S1} [C1|S1,T1] [S1] ><sum {S2} [C2|S2,T2] [S2] >>"

g8_queries = [g8_q1, g8_q2, g8_q3, g8_q4]
g8_answers = [g8_a1, g8_a2, g8_a3, g8_a4]

#########################################

all_tests = [
    {
        "queries": g1_queries,
        "answers": g1_answers,
        "g": g_1,
        "as_string": g_1_string,
    }, {
        "queries": g2_queries,
        "answers": g2_answers,
        "g": g_2,
        "as_string": g_2_string,
    }, {
        "queries": g3_queries,
        "answers": g3_answers,
        "g": g_3,
        "as_string": g_3_string,
    }, {
        "queries": g4_queries,
        "answers": g4_answers,
        "g": g_4,
        "as_string": g_4_string,
    }, {
        "queries": g5_queries,
        "answers": g5_answers,
        "g": g_5,
        "as_string": g_5_string,
    }, {
        "queries": g6_queries,
        "answers": g6_answers,
        "g": g_6,
        "as_string": g_6_string,
    }, {
        "queries": g7_queries,
        "answers": g7_answers,
        "g": g_7,
        "as_string": g_7_string,
    }, {
        "queries": g8_queries,
        "answers": g8_answers,
        "g": g_8,
        "as_string": g_8_string,
    }
]


def tests():

    debug = False
    proof = False

    for index, problem_set in enumerate(all_tests, start=1):

        print("*" * 20, f"Beginning Graph {index}", "*" * 20)

        g = problem_set["g"]
        p = P(g)

        # Verify Graph-Parsing
        g_str = problem_set["as_string"]

        print(f"Graph String: {index}")
        print(g_str)
        parsed = parse_graph_string(g_str)

        print("Original:", g)
        print("  Parsed:", parsed)
        assert g == parsed

        # Verify ID
        for i, (query, answer) in enumerate(zip(problem_set["queries"], problem_set["answers"]), start=1):

            y, x = query

            query_str = f"{', '.join(y)} | {', '.join(x)}"
            print(f"Beginning problem: {query_str}")

            result = ID(y, x, p, g, debug, proof)

            simplify = simplify_expression(result, g, debug)

            if debug:
                print("Debugged Original / Simplified")
                debugPExpr(result)
                debugPExpr(simplify)

            print(f"{query_str} (Original)   = {result}")
            print(f"{query_str} (Simplified) = {simplify}")
            print(f"expected g{index}_a{i} = ", end="")
            print(answer)

            print("*********** REPRODUCE")
            print(simplify.proof())

            with open(f"graph_{index}_{i}.txt", "w") as f:
                f.write(simplify.proof())

            print("*" * 40)
    print("*" * 20, "all done", "*" * 20)


if __name__ == "__main__":
    tests()
