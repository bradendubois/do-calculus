#########################################################
#                                                       #
#   VariableStructures.py                               #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

from re import findall, sub    # Used to parse a line of text into respective Outcomes and Interventions


class Outcome:
    """
    A basic "Outcome" of a variable, representing a specific outcome such as "X = x".
    This does essentially act as a Pair<string, string>-like.
    """

    def __init__(self, name: str, outcome: str):
        """
        Constructor for an Outcome
        @param name: The name of the variable. Ex: "X"
        @param outcome: The specific outcome of the variable. Ex: "x" or "~x"
        """
        self.name = name.strip()
        self.outcome = outcome.strip()

    def __str__(self) -> str:
        return self.name + " = " + self.outcome

    def __hash__(self) -> int:
        return hash(self.name + self.outcome)

    def __copy__(self):
        return Outcome(self.name, self.outcome)

    def copy(self):
        return self.__copy__()

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return self.name == other
        return self.name == other.name and self.outcome == other.outcome


class Variable:
    """
    Represents a basic "Variable", as part of a Conditional Probability Table or the like.
    Has a name, list of potential outcomes, and some list of parent variables.
    """

    def __init__(self, name: str, outcomes: list, parents: list, reach=None, topological_order=0):
        """
        A basic Variable for use in a CPT or Causal Graph
        @param name: The name of the Variable, "X"
        @param outcomes: A list of all potential outcomes of the variable: ["x", "~x"]
        @param parents: A list of strings representing the names of all the parents of this Variable
        @param reach: An optional set of Variables which are reachable from this Variable
        @param topological_order: Used in the ordering of Variables as defined by a topological sort
        """
        self.name = name.strip()
        self.outcomes = [outcome.strip() for outcome in outcomes]
        self.parents = [parent.strip() for parent in parents]
        self.topological_order = topological_order

        if reach is None:
            reach = set()
        self.reach = reach

    def __str__(self) -> str:
        return self.name + ": <" + ",".join(self.outcomes) + ">, <-- " + ",".join(self.parents)

    def __hash__(self) -> int:
        return hash(self.name + str(self.outcomes) + str(self.parents))

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return self.name == other

        return self.name == other.name and \
            set(self.outcomes) == set(other.outcomes) and \
            set(self.parents) == set(other.parents)

    def __copy__(self):
        return Variable(self.name, self.outcomes.copy(), self.parents.copy(), reach=self.reach.copy())

    def copy(self):
        return self.__copy__()


class Intervention(Outcome):
    """
    Represents an intervention; do(X).
    """

    def __init__(self, name: str, fixed_outcome: str):
        super().__init__(name, fixed_outcome)

    def __str__(self) -> str:
        return "do(" + self.name + "=" + self.outcome + ")"

    def __hash__(self):
        return hash(self.name + self.outcome)

    def __copy__(self):
        return Intervention(self.name, self.outcome)

    def copy(self):
        return self.__copy__()


def parse_outcomes_and_interventions(line: str) -> set:
    """
    Take one string line and parse it into a list of Outcomes and Interventions
    @param line: A string representing the query
    @return: A list, of Outcomes and/or Interventions
    """
    # "do(X=x)", "do(X=x, Y=y)", "do(X-x), do(Y=y)" are all valid ways to write interventions
    interventions_preprocessed = findall(r'do\([^do]*\)', line)
    interventions_preprocessed = [item.strip("do(), ") for item in interventions_preprocessed]
    interventions = []
    for string in interventions_preprocessed:
        interventions.extend([item.strip(", ") for item in string.split(", ")])

    # Remove all the interventions, leaving only specific Outcomes
    outcomes_preprocessed = sub(r'do\([^do]*\)', '', line).strip(", ").split(",")
    outcomes_preprocessed = [item.strip(", ") for item in outcomes_preprocessed]
    outcomes = [string for string in outcomes_preprocessed if string]

    # Convert the outcome and intervention strings into the specific Outcome and Intervention classes
    outcomes = [Outcome(item.split("=")[0].strip(), item.split("=")[1].strip()) for item in outcomes]
    interventions = [Intervention(item.split("=")[0].strip(), item.split("=")[1].strip()) for item in interventions]

    together = []
    together.extend(outcomes)
    together.extend(interventions)

    return set(together)
