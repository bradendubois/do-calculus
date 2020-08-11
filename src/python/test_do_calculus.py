from probability_structures.do_calculus.application.rules.DoCalculusRules import *
from probability_structures.do_calculus.application.rules.StandardInferenceRules import *
from probability_structures.do_calculus.ids_ai.IDS_Solver import IDSSolver
from util.parsers.GraphLoader import parse_graph_file_data

# Testing the first 3 tasks page ~88 of Causality

# Fix imports when running this by moving this to the root of the project


def print_query(*packed_query):
    for q in packed_query:
        print(str(q) + " ", end="")
    print()


# Parse the file
parsed = parse_graph_file_data("src/python/graphs/full/causal_graph_6.json")
g = parsed["graph"]

# Task 1 : z | do(x)

# Do it by hand, a la Pearl
print("Doing Task 1 manually.")

# Begin
query = [Query({"Z"}, QueryBody({"X"}, set()))]
print_query("Task 1:", *query)

# 3.34
query = [apply_rule_2(g, query[0].head, query[0].body.interventions, {"X"}, query[0].body.observations)]
print_query("3.34:", *query)

# Repeat Task 1
print("\nCan the IDS Solver do it?")
start = IDSSolver(g, {"Z"}, {"X"}, set())
start.u = {"U"}
result = start.solve()
print(str(result))

# Done
print("\n***************************\n")

# Task 2 : y | do(z)

# Do it by hand, a la Pearl
print("Doing Task 2 manually.")

# Begin
query = [Query({"Y"}, QueryBody({"Z"}, set()))]
print_query("Task 2:", *query)

# 3.35
query = [*condition(g, query[0].head, query[0].body.interventions, {"X"}, query[0].body.observations)]
print_query("3.35:", *query)

# 3.36
query[2] = apply_rule_3(g, query[2].head, query[2].body.interventions, {"Z"}, query[2].body.observations)
print_query("3.36:", *query)

# 3.37
query[1] = apply_rule_2(g, query[1].head, query[1].body.interventions, {"Z"}, query[1].body.observations)
print_query("3.37:", *query)

# Repeat Task 2
print("\nCan the IDS Solver do it?")
start = IDSSolver(g, {"Y"}, {"Z"}, set())
start.u = {"U"}
result = start.solve()
print(str(result))

# Done
print("\n***************************\n")

# Task 3 : y | do(x)

# Do it by hand, a la Pearl
print("Doing Task 3 manually.")

# Begin
query = [Query({"Y"}, QueryBody({"X"}, set()))]
print_query("Task 3:", *query)

# 3.39
query = [*condition(g, query[0].head, query[0].body.interventions, {"Z"}, query[0].body.observations)]
print_query("3.39:", *query)

# 3.34
query[2] = apply_rule_2(g, query[2].head, query[2].body.interventions, {"X"}, query[2].body.observations)
print_query("3.34:", *query)

# 3.40
query[1] = apply_rule_2(g, query[1].head, query[1].body.interventions, {"Z'"}, query[1].body.observations)
print_query("3.40:", *query)

# 3.41
result = apply_rule_3(g, query[1].head, query[1].body.interventions, {"X"}, query[1].body.observations)
query = [query[0]] + [result] + query[2:]
print_query("3.41:", *query)

# Re-compute Task 2
result = [*condition(g, query[1].head, query[1].body.interventions, {"X"}, query[1].body.observations)]
query = [*query[0:1]] + [*result] + [*query[2:]]
print_query("3.35:", *query)

# 3.36
result = apply_rule_3(g, query[3].head, query[3].body.interventions, {"Z'"}, query[3].body.observations)
query = query[0:3] + [result] + query[4:]
print_query("3.36:", *query)

# Done: 3.42
result = apply_rule_2(g, query[2].head, query[2].body.interventions, {"Z'"}, query[2].body.observations)
query = query[0:2] + [result] + query[3:]
print_query("3.42:", *query)


# Repeat Task 1
print("\nTask 1: Can the IDS Solver do it?")
start = IDSSolver(g, {"Z"}, {"X"}, set())
start.u = {"U"}
result = start.solve()
print(str(result))


# Repeat Task 2
print("\nTask 2: Can the IDS Solver do it?")
start = IDSSolver(g, {"Y"}, {"Z"}, set())
start.u = {"U"}
result = start.solve()
print(str(result))


# Repeat Task 3
print("\nTask 3: Can the IDS Solver do it?")
start = IDSSolver(g, {"Y"}, {"X"}, set())
start.u = {"U"}
result = start.solve()
print(str(result))


# Task 4
print("\nTask 4: Can the IDS Solver do it?")
start = IDSSolver(g, {"Y", "Z"}, {"X"}, set())
start.u = {"U"}
result = start.solve()
print(str(result))


# Task 5
print("\nTask 5: Can the IDS Solver do it?")
start = IDSSolver(g, {"X", "Y"}, {"Z"}, set())
start.u = {"U"}
result = start.solve()
print(str(result))





print("\n\n\n********\n\n\n")

# Evaluate each of P(Y|X)

# Load the final query object
# parsed["ql"] = result.result

# y | x
# parsed["known"] = {"Y": "y", "X": "x"}
# print(ql_probability(**parsed))

# y | ~x
# parsed["known"] = {"Y": "y", "X": "~x"}
# print(ql_probability(**parsed))

# ~y | x
# parsed["known"] = {"Y": "~y", "X": "x"}
# print(ql_probability(**parsed))

# ~y | ~x
# parsed["known"] = {"Y": "~y", "X": "~x"}
# print(ql_probability(**parsed))

