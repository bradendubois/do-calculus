from do_calculus.application.DoCalculusRulesRevised import *
from do_calculus.ids_ai.IDS_Solver import IDSSolver
from utilities.parsing.GraphLoader import parse_graph_file_data


# Fix imports when running this by moving this to the root of the project

def print_query(*packed_query):
    for q in packed_query:
        print(str(q) + " ", end="")
    print()


# Parse the file
parsed = parse_graph_file_data("causal_graphs/causal_graph_6.json")
g = parsed["graph"]


# Task 1 : z | do(x)

# Begin
query = [Query({"Z"}, VariableSet({"X"}, set()))]
print_query("Task 1:", *query)

# 3.34
query = [apply_rule_2(g, query[0].head, query[0].body.interventions, {"X"}, query[0].body.observations)]
print_query("3.34:", *query)

# Repeat Task 1
start = IDSSolver(g, {"Z"}, {"X"}, set())
result = start.solve()
print("IDS Solved:", result.success, str(result.result))

# Done
print("\n")

# Task 2 : y | do(z)

# Begin
query = [Query({"Y"}, VariableSet({"Z"}, set()))]
print_query("Task 2:", *query)

# 3.35
query = [*apply_secret_rule_4(g, query[0].head, query[0].body.interventions, {"X"}, query[0].body.observations)]
print_query("3.35:", *query)

# 3.36
query[2] = apply_rule_3(g, query[2].head, query[2].body.interventions, {"Z"}, query[2].body.observations)
print_query("3.36:", *query)

# 3.37
query[1] = apply_rule_2(g, query[1].head, query[1].body.interventions, {"Z"}, query[1].body.observations)
print_query("3.37:", *query)

# Repeat Task 2
start = IDSSolver(g, {"Y"}, {"Z"}, set())
result = start.solve()
print(str(result))

# Done
print("\n")

# Task 3 : y | do(x)

# Begin
query = [Query({"Y"}, VariableSet({"X"}, set()))]
print_query("Task 3:", *query)

# 3.39
query = [*apply_secret_rule_4(g, query[0].head, query[0].body.interventions, {"Z"}, query[0].body.observations)]
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
# HERE
# Re-compute Task 2
result = [*apply_secret_rule_4(g, query[1].head, query[1].body.interventions, {"X"}, query[1].body.observations)]
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

# Repeat Task 2
start = IDSSolver(g, {"Y"}, {"X"}, set())
result = start.solve()
print(str(result))
