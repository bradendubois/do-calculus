from probability.structures.CausalGraph import *


def power_set(variable_list):
    """
    Quick helper that creates a chain of tuples, which will be the power set of the given list
    :param variable_list: A list of string variables
    :return: A chain object of tuples; power set of variable_list
    """
    p_set = list(variable_list)
    return itertools.chain.from_iterable(itertools.combinations(p_set, r) for r in range(len(p_set)+1))


head = [Outcome("Xj", "xj")]

body1 = [Intervention("Xi", "xi"), Intervention("X3", "x3"), Intervention("X5", "x5")]
body2 = [Intervention("Xi", "xi"), Outcome("X3", "x3"), Outcome("X5", "x5")]

for _ in range(100):

    for s in power_set(body1):
        print("instantiating new CG")
        cg = CausalGraph("full/causal_graph_5.json")

        x = {"Xj"}
        y = set([i.name for i in body1])

        print("getting z's")
        deconfounders = BackdoorController(cg.variables).all_dcf_sets(y, x)
        deconfounders = [s for s in deconfounders if not any(g.name in s for g in body1 if not isinstance(g, Intervention))]

        cg.probability_query_with_interventions(head, body1, deconfounders)


for _ in range(100):

    for s in power_set(body2):
        print("instantiating new CG")
        cg = CausalGraph("full/causal_graph_5.json")

        x = {"Xj"}
        y = set([i.name for i in body2])

        print("getting z's")
        deconfounders = BackdoorController(cg.variables).all_dcf_sets(y, x)
        deconfounders = [s for s in deconfounders if not any(g.name in s for g in body2 if not isinstance(g, Intervention))]

        cg.probability_query_with_interventions(head, body2, deconfounders)
