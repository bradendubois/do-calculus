#!/usr/bin/env python

import itertools

from probability.structures.Graph import Graph
from probability.structures.CausalGraph import CausalGraph
from util.parsers.GraphLoader import parse_graph_file_data

from ID_algorithm import ID, ProbabilityDistribution, latent_projection

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

