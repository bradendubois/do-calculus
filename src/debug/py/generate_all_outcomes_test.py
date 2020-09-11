from probability_structures.CausalGraph import *

vars = [["a", "~a"], ["b", "~b"], ["c", "~c"]]

outcomes = itertools.product(*vars)

tests = []

cg = CausalGraph("full/simulation.json")

for outcome in outcomes:
    arg = "A = " + outcome[0] + ", B = " + outcome[1] + ", C = " + outcome[2]
    tests.append({
        "name": "Probability Test: P(" + "".join(outcome) + ")",
        "type": "probability",
        "args": [
            arg
        ],
        "expected_result": cg.probability(parse_outcomes_and_interventions(arg), [])
    })

with open("test_file", "w") as f:
    json.dump({"tests": tests}, f)
