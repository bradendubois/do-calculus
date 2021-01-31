from src.probability.structures.CausalGraph import CausalGraph
from src.probability.structures.VariableStructures import parse_outcomes_and_interventions


def api_probability_query(cg: CausalGraph, query: str) -> float:
    """
    Compute a probability query for the currently loaded causal graph.

    Parameters
    ----------
    cg: A Causal Graph containing variables, distributions, etc.
    query: A string of the form "V = v, Y=y, X=x | W=w", where each variable on the left of an equals
        symbol is a variable in the Causal Graph provided, and the value on the right is a possible
        outcome of the given variable

    Returns
    -------
    Returns a value in the range [0.0, 1.0] corresponding to the given probability

    Raises
    -------
    ProbabilityException
        For when the given probability can not be computed, due to an undefined variable, etc.
    """

    l, r = query.split("|") if "|" in query else query, []
    head = parse_outcomes_and_interventions(l)
    body = parse_outcomes_and_interventions(r) if isinstance(r, str) else r
    return cg.probability_query(head, body)
