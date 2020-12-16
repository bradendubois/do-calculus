import itertools
import random

from graph_generator import generate_graph
from probability.structures.CausalGraph import CausalGraph
from tests.RegressionTesting import basic_validation
from util.parsers.GraphLoader import parse_graph_file_data


def sum_to(x, y):

    left = y
    nums = []

    for i in range(x-1):
        select = random.randrange(left)
        left -= select
        nums.append(select)
    nums.append(left)

    assert sum(nums) == y, "Should sum to " + str(y) + " but sum to " + str(sum(nums))

    return nums


def generate_distribution(graph):

    variables = {}

    for v in graph.v:

        outcome_list = [v.lower(), "~" + v.lower()]
        parent_list = sorted(list(graph.parents(v)))

        cur = {
            "name": v,
            "outcomes": outcome_list,
            "parents": parent_list,
            "determination": {
                "type": "table"
            }
        }

        variables[v] = cur


    for v in graph.v:

        distribution = []

        outcomes = variables[v]["outcomes"]
        parent_outcomes = [variables[p]["outcomes"] for p in sorted(graph.parents(v))]

        for cross in itertools.product(*parent_outcomes):

            nums = sum_to(len(outcomes), 10000)

            for i, outcome in enumerate(outcomes):
                distribution.append([outcome, list(cross), nums[i] / 10000])

        variables[v]["determination"]["table"] = distribution

    return variables

g = generate_graph()
temp = generate_distribution(g)

print(g)

for k in temp:
    print(k, temp[k])

r = CausalGraph(**parse_graph_file_data({"variables": list(temp.values())}))

error, message = basic_validation(r, "none")
print(error, message)
