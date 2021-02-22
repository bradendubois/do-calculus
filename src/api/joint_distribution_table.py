from itertools import product
from src.probability.structures.CausalGraph import CausalGraph
from src.probability.structures.VariableStructures import Outcome


def api_joint_distribution_table(cg: CausalGraph) -> list:
    """
    Compute and return a joint distribution table for the given model.
    @param cg: A CausalGraph to compute the JDT for.
    @return: A list of sets, where each item is a tuple, (Outcomes, P), where the first item is a set containing one
        Outcome object for each variable in the model, and the second is the respective probability.
    """
    sorted_keys = sorted(cg.variables.keys())
    results = []

    for cross in product(*list(map(lambda x: cg.outcomes[x], sorted_keys))):
        outcomes = {Outcome(x, cross[i]) for i, x in enumerate(sorted_keys)}
        results.append((outcomes, cg.probability_query(outcomes, set())))

    return results
