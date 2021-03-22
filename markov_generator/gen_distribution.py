import itertools
import random

from do.structures import Graph


def sum_to(x, y):

    left = y
    nums = []

    for _ in range(x-1):
        select = random.randrange(left)
        left -= select
        nums.append(select)
    nums.append(left)

    assert sum(nums) == y, "Should sum to " + str(y) + " but sum to " + str(sum(nums))

    return nums


def generate_distribution(graph: Graph):

    variables = {}

    for v in graph.v:

        outcome_list = [v.lower(), "~" + v.lower()]
        parent_list = sorted(list(graph.parents(v)))

        cur = {
            "outcomes": outcome_list,
            "parents": parent_list,
        }

        variables[v] = cur

    for v in graph.v:

        distribution = []

        outcomes = variables[v]["outcomes"]
        parent_outcomes = [variables[p]["outcomes"] for p in sorted(graph.parents(v))]

        for cross in itertools.product(*parent_outcomes):

            nums = sum_to(len(outcomes), 10000)

            for i, outcome in enumerate(outcomes):
                distribution.append([outcome, *list(cross), nums[i] / 10000])

        variables[v]["table"] = distribution

    return variables
