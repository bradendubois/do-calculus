#########################################################
#                                                       #
#   VariableStructures.py                               #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################


class Outcome:
    """
    A basic "Outcome" of a variable, representing a specific outcome such as "X = x".
    This does essentially act as a Pair<string, string>-like.
    """

    def __init__(self, name: str, outcome: str):
        """
        Constructor for an Outcome
        :param name: The name of the variable. Ex: "X"
        :param outcome: The specific outcome of the variable. Ex: "x" or "~x"
        """
        self.name = name.strip()
        self.outcome = outcome.strip()

    def __str__(self) -> str:
        return self.name + " = " + self.outcome

    def __hash__(self) -> int:
        return hash(self.name + self.outcome)

    def __eq__(self, other) -> bool:
        return self.name == other.name and self.outcome == other.outcome


class Variable:
    """
    Represents a basic "Variable", as part of a Conditional Probability Table or the like.
    Has a name, list of potential outcomes, and some list of parent variables.
    """

    def __init__(self, name: str, outcomes: list, parents: list, reach=None):
        """
        A basic Variable for use in a CPT or Causal Graph
        :param name: The name of the Variable, "X"
        :param outcomes: A list of all potential outcomes of the variable: ["x", "~x"]
        :param parents: A list of strings representing the names of all the parents of this Variable
        :param reach: An optional set of Variables which are reachable from this Variable
        """
        self.name = name.strip()
        self.outcomes = [outcome.strip() for outcome in outcomes]
        self.parents = [parent.strip() for parent in parents]

        if reach is None:
            reach = set()
        self.reach = reach

    def __str__(self) -> str:
        return self.name + ": <" + ",".join(self.outcomes) + ">, <-- " + ",".join(self.parents)

    def __hash__(self) -> int:
        return hash(self.name + str(self.outcomes) + str(self.parents))

    def __eq__(self, other) -> bool:
        return self.name == other.name and \
               set(self.outcomes) == set(other.outcomes) and \
               set(self.parents) == set(other.parents)

    def __copy__(self):
        return Variable(self.name, self.outcomes.copy(), self.parents.copy(), reach=self.reach.copy())

    def copy(self):
        return self.__copy__()
