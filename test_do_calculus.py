from do_calculus.application.DoCalculusRulesRevised import *
from do_calculus.ids_ai.IDS_Solver import IDSSolver
from utilities.parsing.GraphLoader import parse_graph_file_data


# Fix imports when running this by moving this to the root of the project


parsed = parse_graph_file_data("causal_graphs/causal_graph_6.json")
g = parsed["graph"]

# Task 1

y, x, w = {"Z"}, {"X"}, set()
z = {"X"}

result = rule_2_applicable(g, y, x, z, w)
print("Rule 2 applied to task 1:", result)
result = apply_rule_2(g, y, x, z, w)
print("Result:", str(result))

# solver = IDSSolver(g, y, x, w)

#

#


# Task 2 : y | do(z)

print("\n\n\n")

# Insert x as observation
y, x, w = {"Y"}, {"Z"}, set()
z = {"X"}

print("Jeffreys: Can Insert X:", secret_rule_4_applicable(g, y, x, z, w))
result = apply_secret_rule_4(g, y, x, z, w)
print("Result:", " ".join([str(i) for i in result]))

print("Rule 3: Can Delete do(Z) from x | do(Z):", rule_3_applicable(g, y, x, z, w))
mod = result[2]
new_result = apply_rule_3(g, mod.head, mod.body.interventions, {"Z"}, mod.body.observations)
print("Result:", str(result))
print(str(result[0]), str(result[1]), str(new_result))

delete_mod = result[1]
y, x, w = delete_mod.head, delete_mod.body.interventions, delete_mod.body.observations
z = {"Z"}
print("Rule 2: Can drop do(Z) to Z from y | x, do(Z):", rule_2_applicable(g, y, x, z, w))
newest_result = apply_rule_2(g, y, x, z, w)
print("Result:", str(newest_result))

print(str(result[0]), str(newest_result), str(new_result))

print("\n\n\n\n")

# Task 3

y, x, w = {"Y"}, {"X"}, set()

solver = IDSSolver(parsed["graph"], y, x, w)

result = solver.solve()

if result.success:
    print(" ".join(str(i) for i in result.data))
