from typing import Collection, Dict, Union

from ..structures.CausalGraph import CausalGraph
from ..structures.VariableStructures import Outcome, Intervention, parse_outcomes_and_interventions


def api_probability_query_parse(query: str) -> Dict[str, Collection[str]]:
    """
    Parse a query string into Outcome and Intervention structures.
    @param query: A string of the form "Y=y, X=x | W=w", or just "Y=y, X=x"
    @return A dictionary mapping "head" and "body" to lists of Outcome and Intervention objects
    """
    if "|" in query:
        l, r = query.split("|")
        return {
            "y": parse_outcomes_and_interventions(l),
            "x": parse_outcomes_and_interventions(r)
        }

    return {
        "y": parse_outcomes_and_interventions(query),
        "x": set()
    }


def api_probability_query(cg: CausalGraph, y: Collection[Outcome], x: Collection[Union[Outcome, Intervention]]) -> float:
    """
    Compute a probability query for the currently loaded causal graph.
    @param cg: A Causal Graph containing variables, distributions, etc.
    @param y: A set of Outcome objects that exist in the given Causal Graph
    @param x: A set of Outcome and/or Intervention objects that exist in the given Causal Graph
    @return A value in the range [0.0, 1.0] corresponding to the given probability
    @raise ProbabilityException when the given probability can not be computed, due to an undefined variable, etc.
    """
    return cg.probability_query(y, x)
