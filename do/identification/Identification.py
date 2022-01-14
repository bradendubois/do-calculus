from typing import List, Optional, Set, Tuple, Union

from .Exceptions import Fail as FAIL
from .LatentGraph import LatentGraph as Graph
from .PExpression import PExpression, TemplateExpression


# noinspection PyPep8Naming
def Identification(y: Set[str], x: Set[str], p: PExpression, g: Graph, prove: bool = True, i=0, passdown_proof: Optional[List[Tuple[int, List[str]]]] = None) -> PExpression:

    def s(a_set):
        if len(a_set) == 0:
            return "Ø"
        return "{" + ', '.join(a_set) + "}"

    # The continuation of a proof that is ongoing if this is a recursive ID call, or a 'fresh' new proof sequence otherwise
    proof_chain = passdown_proof if passdown_proof else []

    # noinspection PyPep8Naming
    def An(vertices):
        return g.ancestors(vertices)

    if prove:
        proof_chain.append((i, [f"ID Begin: Y = {s(y)}, X = {s(x)}"]))

    # 1
    if x == set():
        if prove:
            proof_chain.append((i, [
                "1: if X == Ø, return Σ_{V \\ Y} P(V)",
                f"  --> Σ_{s(g.V - y)} P({s(g.V)})",
                "",
                f"[***** Standard Probability Rules *****]"
            ]))

        return p_operator(g.V - y, p, proof_chain)

    # 2
    if g.V != An(y):
        w = g.V - An(y)
        if prove:
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

        return Identification(y, x & An(y), p_operator(g.V - g[An(y)].V, p), g[An(y)], prove, i+1, proof_chain)


    # 3
    w = (g.V - x) - g.without_incoming(x).ancestors(y)

    if prove:
        proof_chain.append((i, [
            "let W = (V \\ X) \\ An(Y)_G_X",
            f"--> W = ({s(g.V)} \\ {s(x)}) \\ An({s(y)})_G_{s(x)}",
            f"--> W = {s(g.V - x)} \\ {s(g.without_incoming(x).ancestors(y))}",
            f"--> W = {s(w)}"
        ]))

    if w != set():
        if prove:
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

        return Identification(y, x | w, p, g, prove, i+1, proof_chain)

    C_V_minus_X = g[g.V - x].C

    # Line 4
    if len(C_V_minus_X) > 1:
        if prove:
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

        return PExpression(g.V - (y | x), [Identification(s_i, g.V - s_i, p, g, prove, i+1) for s_i in C_V_minus_X], proof_chain)

    else:

        # At this point we have a single component
        S = C_V_minus_X[0]

        if prove:
            proof_chain.append((i, [
                "if C(G \\ X) = {S}",
                f"--> C({s(g.V)} \\ {s(x)}) = {s(S)}"
            ]))

        # Line 5
        if set(S) == g.V:
            if prove:
                proof_chain.append((i, [
                    "5: if C(G) = {G}: FAIL(G, S)",
                    f"--> G, S form hedges F, F' for Px(Y) -> {g}, {S} for P_{x}({y})"
                ]))

            raise FAIL(g, S, proof_chain)

        # Line 6 - a single c-component
        if S in g.C:

            dists = []
            dist_str = []
            for vi in S:
                given = g.v_Pi[:g.v_Pi.index(vi)]
                if prove:
                    dist_str.append(f"P({vi})" if len(given) == 0 else f"P({vi} | {', '.join(given)})")
                dists.append(TemplateExpression(vi, given))

            if prove:
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

            return PExpression(S - y, dists, proof_chain)

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
                p.append(TemplateExpression(v, rhs))
                if prove:
                    msg += f"[{v}{(f' | ' + ', '.join(rhs)) if len(rhs) > 0 else ''}]"

            g_s_prime = g[s_prime]

            if prove:
                proof_chain.append((i, [
                    f"7: if ∃(S') S ⊂ S' ∈ C(G)",
                    f"--> let S = {s(S)}, S' = {s(s_prime)}",
                    f"--> {s(S)} ⊂ {s(s_prime)} ∈ {', '.join(list(map(s, g.C)))}",
                    "  return ID(y, x ∩ S', π_{V_i ∈ S'} P(V_i | V_π^(i-1) ∩ S', V_π^(i-1) \\ S'), S')",
                    msg,
                    f"  --> ID({s(y)}, {s(x)} ∩ {s(s_prime)}, P, G = ({g_s_prime.V}, {g_s_prime.e}, {g_s_prime.e_bidirected}))",
                    "",
                    "  [***** Proof *****]",
                    f"  G is partitioned into X = {s(x)} and S = {s(S)}, where X ⊂ An(S).",
                    "  M_{X \\ S'} induces G \\ (X \\ S') = S'.",
                    "  P_{x} = P_{x ∩ S', X \\ S'} = P_{x ∩ S'}.",
                ]))

            return Identification(y, x & s_prime, PExpression([], p), g_s_prime, prove, i+1, proof_chain)


def simplify_expression(original: PExpression, g: Graph, debug=False) -> PExpression:

    def _simplify(current,i = 0):

        cpt_list_copy = list(filter(lambda i: isinstance(i, TemplateExpression), current.terms))
        for s in current.terms:

            if isinstance(s, TemplateExpression):
                continue

            c = _simplify(s, i + 1)

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
                x = {expression.head}
                for variable in expression.given:
                    y = {variable}
                    z = set(expression.given) - y
                    if g.ci(x, y, z):
                        msg1 = f"{', '.join(x)} is independent of {', '.join(y)} given {', '.join(z)}, and can be removed."
                        msg2 = f"p operator removed {variable} from body of {expression}"
                        if debug:
                            print(msg1)
                            print(msg2)
                        steps.append(msg1)
                        expression.given.remove(variable)
                        removed_one = True

                if not removed_one:
                    break
        # """

        # Remove unnecessary expressions
        # """
        while True:
            bodies = set().union(*[el.given for el in current.terms if isinstance(el, TemplateExpression)])
            search = filter(lambda el: isinstance(el, TemplateExpression) and el.head in current.sigma, current.terms)
            remove = list(filter(lambda el: el.head not in bodies, search))

            if len(remove) == 0:
                break

            for query in remove:
                current.sigma.remove(query.head)
                current.terms.remove(query)
                msg = f"{query.head} can be removed."
                if debug:
                    print(msg)
                steps.append(msg)
        # """

        while True:
            sumout = [cpt for cpt in current.terms if isinstance(cpt, TemplateExpression) and cpt.head in current.sigma and not any([cpt.head in el.given for el in current.terms if isinstance(el, TemplateExpression)])]
            if not sumout:
                break
            for cpt in sumout:
                current.terms.remove(cpt)
                current.sigma.remove(cpt.head)

        if len(steps) > 0:
            tables = ", ".join(f"P({table.head} | {', '.join(table.given)})" if len(table.given) > 0 else f"P({table.head})" for table in cpt_list_copy)
            steps.append(f"After simplification: {tables}")

        def distribution_position(item: Union[PExpression, TemplateExpression]):
            if isinstance(item, PExpression):
                if len(item.sigma) == 0:
                    return len(g.v_Pi)
                return len(g.v_Pi) + min(0, *list(map(lambda v: g.v_Pi.index(v), item.sigma)))
            else:
                return g.v_Pi.index(item.head)

        # Sort remaining expressions by the topological ordering
        current.terms.sort(key=distribution_position)

        if len(steps) > 0:
            steps.insert(0, "[***** Simplification *****]")

        return steps

    if original.internal_proof:
        depth = original.internal_proof[-1][0] + 1
    else:
        depth = 1

    p = original.copy()
    changes = _simplify(p)
    p.internal_proof.append((depth, changes))
    return p


def p_operator(v: Set[str], p: PExpression, proof: List[Tuple[int, List[str]]] = None):
    return PExpression(list(v.copy() | set(p.sigma)), p.terms.copy(), proof)
