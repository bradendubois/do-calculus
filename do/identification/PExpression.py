from typing import List, Sequence, Tuple

from .LatentGraph import Graph

SUM = "+"
MUL = "*"

class PExpr:

    def __init__(self, vs, ps: list = None, proof: List[Tuple[int, List[str]]] = None):
        self.sigma = list(vs)
        self.terms = list(ps) if ps else []
        self.internal_proof = proof if proof else []

    def __str__(self):

        buf = ""
        if self.sigma:
            buf += "<sum {" + ", ".join(self.sigma) + "} "

        # Put Distributions (or PExprs with empty summations) first
        for el in filter(lambda x: isinstance(x, TemplateExpression) or isinstance(x, PExpr) and len(x.sigma) == 0, self.terms):
            buf += str(el)

        # Put PExprs after
        for el in filter(lambda x: isinstance(x, PExpr) and len(x.sigma) > 0, self.terms):
            buf += str(el)

        if self.sigma:
            buf += '>'
        return buf

    def pexpr_copy(self):
        copied_contents = []
        for item in self.terms:
            if isinstance(item, PExpr):
                copied_contents.append(item.pexpr_copy())
            else:
                copied_contents.append(item.copy())
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

        for child in filter(lambda x: isinstance(x, PExpr), self.terms):
            s += child.proof()
        return s


# noinspection PyPep8Naming
def P(g: Graph) -> PExpr:
    return PExpr([], [TemplateExpression(x, list(g.Parents[x])) for x in g.V])



class TemplateExpression:
    

    def __init__(self, head: str, given: Sequence[str]) -> None:
        self.head = head
        self.given = given

    def copy(self):
        return TemplateExpression(self.head, [x for x in self.given])
    
    def __str__(self) -> str:
        if len(self.given) == 0:
            return f"[{self.head}]"
        return f"[{self.head}|{','.join(self.given)}]"
