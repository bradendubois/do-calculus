#########################################################
#                                                       #
#   Distribution                                        #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# A representation of probability distributions for use in Shpitser's ID algorithm

class JointDistribution:
    """
    A dictionary, mapping a variable to its probability distribution
    """

    def __init__(self, tables: dict, given=None):
        self.tables = tables
        self.given = given

    def __call__(self, x, predecessors=None):
        """
        Get subset X of some ProbabilityDistribution P.
        :param x: A set of variables in some ProbabilityDistribution P.
        :param predecessors: The set of parents of X
        :return: A ProbabilityDistribution of the subset X.
        """

        # Line 1 Return
        if isinstance(x, str) and predecessors is None:
            return JointDistribution({x: self.tables[x]})

        # Line 2 Return
        elif isinstance(x, set) and predecessors is None:
            return JointDistribution({p: self.tables[p] for p in self.tables if p in x})

        # Line 6 return
        elif isinstance(x, str) and predecessors is not None:
            return JointDistribution(self.tables[x], {p: self.tables[p] for p in predecessors})

    def __str__(self):
        if self.tables is None:
            return ""

        if self.given is None:
            return "P(" + ", ".join(list(self.tables.keys())) + ")"
        return "P(" + ", ".join(self.tables.keys()) + " | " + ", ".join(self.given.keys()) + ")"
