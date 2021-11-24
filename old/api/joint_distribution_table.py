from itertools import product

from ..structures.CausalGraph import CausalGraph
from ..structures.ConditionalProbabilityTable import ConditionalProbabilityTable
from ..structures.VariableStructures import Outcome, Variable


def api_joint_distribution_table(cg: CausalGraph) -> ConditionalProbabilityTable:
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

    keys = sorted(cg.variables.keys())
    rows = [[",".join(map(str, outcomes)), [], p] for outcomes, p in results]
    rows.append(["Total:", [], sum(map(lambda r: r[1], results))])
    cpt = ConditionalProbabilityTable(Variable(",".join(keys), [], []), [], rows)

    return cpt
