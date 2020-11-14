#!/usr/bin/env python

import itertools

from probability.structures.Graph import Graph
from probability.structures.CausalGraph import CausalGraph
from probability.structures.VariableStructures import Outcome
from util.parsers.GraphLoader import parse_graph_file_data

from ID_algorithm import ID, ProbabilityDistribution, latent_projection

from ID_algorithm import Symbol, PiObj, SigmaObj


def parse_ID_result(result: Symbol, cg: CausalGraph, known: dict):

    if known is None:
        known = dict()

    # Summation
    if isinstance(result, SigmaObj):
        if result.s is None or len(result.s) == 0:
            if isinstance(result.exp, list):
                i = 0.0
                for item in result.exp:
                    i += parse_ID_result(item, cg, known)
                return i
            return parse_ID_result(result.exp, cg, known)
        else:
            outcomes = list(result.s)
            total = 0
            cross = itertools.product(*[cg.outcomes[v] for v in outcomes])
            for c in cross:
                total = 0
                for o in range(len(outcomes)):
                    known[outcomes[o]] = c[o]

                if isinstance(result.exp, list):
                    for item in result.exp:
                        total += parse_ID_result(item, cg, known)
                else:
                    total += parse_ID_result(result.exp, cg, known)

            return total

    # Product
    elif isinstance(result, PiObj):

        if isinstance(result.exp, list):
            prod = 1.0
            for item in result.exp:
                prod *= parse_ID_result(item, cg, known)
            return prod
        else:
            return parse_ID_result(result.exp, cg, known)

    # Compute probability
    elif isinstance(result, ProbabilityDistribution):
        h = result.tables
        b = result.given

        head = []
        for key in h:
            if key not in known:
                value = cg.outcomes[key][0]
            else:
                value = known[key]
            head.append(Outcome(key, value))

        body = []
        if b is not None:
            for key in b:
                if key not in known:
                    value = cg.outcomes[key][0]
                else:
                    value = known[key]
                body.append(Outcome(key, value))

        return cg.probability_query(head, body)

    else:
        print("UNCERTAIN:", type(result))

"""
# Load the melanoma graph
melanoma_cg = CausalGraph(**parse_graph_file_data("./graphs/full/causal_graph.json"))

print(str(melanoma_cg.graph))
"""

"""
Y = {"Y"}
X = {"X"}
# X = set()
P = ProbabilityDistribution(melanoma_cg.tables)
G = latent_projection(melanoma_cg.graph, set())
"""


"""
test_1 = ID(Y, X, P, G)
for item in test_1:
    if isinstance(item, tuple) or isinstance(item, list):
        print(item[0], *[str(i) for i in item[1:]], end="")
    elif isinstance(item, str):
        print(item, end="")
    else:
        print(type(item))
print()
"""

"""
test_2 = ID(Y, X, P, G)
print(str(test_2))

abcd = CausalGraph(**parse_graph_file_data("./graphs/full/abcd.json"))

abcd_l = latent_projection(abcd.graph, set())

print(str(abcd_l))

result = ID({"A"}, {"C"}, ProbabilityDistribution(abcd.tables), abcd_l)
print("***")
print(str(result))
print("\n***")
"""

melanoma = CausalGraph(**parse_graph_file_data("./graphs/full/causal_graph.json"))

melanoma_l = latent_projection(melanoma.graph, set())

print(str(melanoma_l))

result = ID({"Y"}, {"X", "Z"}, ProbabilityDistribution(melanoma.tables), melanoma_l)

print("***")
print(str(result))

print("Result:", result.exp.exp[0].tables.keys(), result.exp.exp[0].given.keys())
print("\n***")

result = ID({"Z"}, {"X", "Y"}, ProbabilityDistribution(melanoma.tables), melanoma_l)
print("Results: ", result)

result = ID({"Y"}, {"X"}, ProbabilityDistribution(melanoma.tables), melanoma_l)
print("Results: ", result)

print(parse_ID_result(result, melanoma, dict()))
