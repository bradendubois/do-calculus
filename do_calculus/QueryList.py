#########################################################
#                                                       #
#   QueryList                                           #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# A way of representing a list of queries to be multiplied together, some of which may involve Summations

from probability_structures.Graph import Graph
from probability_structures.Probability_Engine import ProbabilityEngine

def rename(s: set):
    return {item + "'" for item in s}

def clean(s: set):
    return {item.strip("'") for item in s}


class Sigma:

    def __init__(self, over: set):
        self.over = over

    def __copy__(self):
        return Sigma(self.over)

    def copy(self):
        return self.__copy__()


class VariableSet:

    def __init__(self, interventions: set, observations: set):
        self.interventions = interventions
        self.observations = observations

    def __copy__(self):
        return VariableSet(self.interventions.copy(), self.observations.copy())

    def copy(self):
        return self.__copy__()




class Query:

    def __init__(self, head: set, body: VariableSet):
        self.head = head
        self.body = body


class ComplexQuery:

    def __init__(self, ):




class QueryList:

    def __init__(self, variables: dict, engine: ProbabilityEngine, regular_queries: list, nested_query_lists: list, depth: int, max_depth: int, sigma=None or str):

        self.variables = variables
        self.engine = engine
        self.regular_queries = regular_queries
        self.nested_query_lists = nested_query_lists
        self.sigma = sigma

        self.depth = depth
        self.max_depth = max_depth

    def fully_resolve(self, rules_applied: set) -> bool:

        # Don't need to break down / change everything
        if self.is_fully_resolved():
            return True

        for option in self.options():



        return False

    def is_fully_resolved(self) -> bool:
        for regular_query in self.regular_queries:


    def resolve(self) -> float:

        # No Sigma
        if self.sigma is None:

            p = 1
            for regular_query in self.regular_queries:
                p *= self.engine.probability(regular_query)

            for further_resolve_query in self.nested_query_lists:
                p *= further_resolve_query.resolve()

        # Summation, expand out
        else:


        return 0.0
