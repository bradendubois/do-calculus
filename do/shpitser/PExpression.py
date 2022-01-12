from typing import List, Tuple

from .LatentGraph import Graph


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
def P(g: Graph) -> PExpr:
    return PExpr([], [[x, list(g.Parents[x])] for x in g.V])
