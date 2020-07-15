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


def union(s1: set, s2: set):
    new_set = set()

    # print("Dirty:", s1, s2)

    for i in s1:
        if clean(i) not in new_set:
            new_set.add(i)
    for i in s2:
        if clean(i) not in new_set:
            new_set.add(i)

    # print("Union:", new_set)
    return new_set


def subtract(s1: set, s2: set):

    # print("Dirty:", s1, s2)
    new_set = set()
    clean_s2 = clean(s2)

    for i in s1:
        if clean(i) not in clean_s2:
            new_set.add(i)

    # print("Subtract:", new_set)
    return new_set


def rename(s: set):
    return {item + "'" for item in s}


def clean(s: set or str):
    if isinstance(s, str):
        return s.strip("'")
    return {item.strip("'") for item in s}


class Sigma:

    def __init__(self, over: set):
        self.over = over

    def __str__(self):
        return "Sigma_" + ",".join(self.over)

    def __copy__(self):
        return Sigma(self.over)

    def copy(self):
        return self.__copy__()


class VariableSet:

    def __init__(self, interventions: set, observations: set):
        self.interventions = interventions
        self.observations = observations

    def __str__(self):
        msg = ""
        if len(self.interventions) > 0:
            msg += "do(" + ",".join(self.interventions) + ")"
        if len(self.interventions) > 0 and len(self.observations) > 0:
            msg += ", "
        if len(self.observations) > 0:
            msg += ",".join(self.observations)
        return msg

    def __copy__(self):
        return VariableSet(self.interventions.copy(), self.observations.copy())

    def copy(self):
        return self.__copy__()


class Query:

    def __init__(self, head: set, body: VariableSet):
        self.head = head
        self.body = body

    def __str__(self):
        msg = "P(" + ",".join(self.head)
        if len(self.body.interventions | self.body.observations) > 0:
            msg += " | " + str(self.body)
        return msg + ")"

    def __copy__(self):
        return Query(self.head.copy(), self.body.copy())

    def copy(self):
        return self.__copy__()

    def resolved(self):
        return len(self.body.interventions) == 0


class QueryList:

    def __init__(self, queries: list):
        # self.variables = variables
        # self.graph = graph
        self.queries = queries

    def __str__(self):
        return " ".join(str(item) for item in self.queries)

    def __copy__(self):
        return QueryList([query.copy() for query in self.queries])
        # return QueryList(self.variables, self.graph, self.queries)

    def copy(self):
        return self.__copy__()

    def fully_resolved(self):
        for item in self.queries:
            if isinstance(item, Query) and not item.resolved():
                return False
        return True











class QueryList2:

    def __init__(self, variables: dict, engine: ProbabilityEngine, regular_queries: list, nested_query_lists: list, depth: int, max_depth: int, sigma=None or str):

        self.variables = variables
        self.engine = engine
        self.regular_queries = regular_queries
        self.nested_query_lists = nested_query_lists
        self.sigma = sigma

        self.depth = depth
        self.max_depth = max_depth



    def resolve(self) -> float:

        # No Sigma
        if self.sigma is None:

            p = 1
            for regular_query in self.regular_queries:
                p *= self.engine.probability(regular_query)

            for further_resolve_query in self.nested_query_lists:
                p *= further_resolve_query.resolve()


        return 0.0
