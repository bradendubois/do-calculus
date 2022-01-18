from do.core.Exceptions import ProbabilityException


class Fail(ProbabilityException):
    """
    Represents a failure for the Identification algorithm to properly
    identify a causal effect. This (real) exception is raised as done
    in the ID algorithm.
    """

    def __init__(self, s, sp, proof):
        super().__init__(s, sp)
        self.proof = proof
