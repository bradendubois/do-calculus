
class Fail(Exception):
    def __init__(self, f, fp, proof):
        super().__init__(f, fp)
        self.proof = proof

