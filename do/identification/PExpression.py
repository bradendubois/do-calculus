from typing import Collection, List, Sequence, Tuple


class PExpression:

    def __init__(self, sigma: Collection[str], terms: list = None, proof: List[Tuple[int, List[str]]] = None):
        self.sigma = list(sigma)
        self.terms = list(terms) if terms else []
        self.internal_proof = proof if proof else []

    def __str__(self):

        buf = ""
        if self.sigma:
            buf += "<Σ {" + ", ".join(self.sigma) + "} "

        # Put Distributions (or PExprs with empty summations) first
        for el in filter(lambda x: isinstance(x, TemplateExpression) or isinstance(x, PExpression) and len(x.sigma) == 0, self.terms):
            buf += str(el)

        # Put PExprs after
        for el in filter(lambda x: isinstance(x, PExpression) and len(x.sigma) > 0, self.terms):
            buf += str(el)

        if self.sigma:
            buf += '>'
        return buf

    def copy(self):
        copied_proof = [(i, [s for s in block]) for i, block in self.internal_proof]
        return PExpression(self.sigma.copy(), [x.copy() for x in self.terms], copied_proof)

    def proof(self) -> str:
        s = ""
        for j, block in self.internal_proof:
            indent = " " * 3 * j
            for line in block:
                s += indent + line + '\n'
            s += '\n'

        for child in filter(lambda x: isinstance(x, PExpression), self.terms):
            s += child.proof()
        return s


class TemplateExpression:
    

    def __init__(self, head: str, given: Sequence[str]) -> None:
        self.head = head
        self.given = given

    def copy(self):
        return TemplateExpression(self.head, self.given.copy())
    
    def __str__(self) -> str:
        if len(self.given) == 0:
            return f"[{self.head}]"
        return f"[{self.head}|{','.join(self.given)}]"
