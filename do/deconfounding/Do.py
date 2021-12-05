from itertools import product
from loguru import logger
from typing import Collection

from ..core.Expression import Expression
from ..core.Inference import inference
from ..core.Model import Model
from ..core.Variables import Outcome, Intervention
from ..core.helpers import p_str

from .Backdoor import backdoors, deconfound
from .Exceptions import NoDeconfoundingSet


def treat(expression: Expression, interventions: Collection[Intervention], model: Model) -> float:
    
    head = set(expression.head())
    body = set(expression.body())

    # If there are no Interventions, we can compute a standard query
    if len(interventions) == 0:
        return inference(expression, model)

    # There are interventions; may need to find some valid Z to compute
    else:

        paths = backdoors(head, body, interventions)

        # No backdoor paths; augment graph space and compute
        if len(paths) == 0:
            expression_transform = Expression(expression.head(), set(expression.body()) | set(Outcome(x.name, x.value) for x in interventions))
            model.graph().disable_incoming(*interventions)
            p = inference(expression_transform, model)
            model.graph().reset_disabled()
            return p

        # Backdoor paths found; find deconfounding set to compute
        # Find all possible deconfounding sets, and use possible subsets
        deconfounding_sets = deconfound(interventions, head, model.graph())

        # Filter down the deconfounding sets not overlapping with our query body
        vertex_dcf = list(filter(lambda s: len(set(s) & {x.name for x in body}) == 0, deconfounding_sets))
        if len(vertex_dcf) == 0:
            raise NoDeconfoundingSet

        # Compute with every possible deconfounding set as a safety measure; ensuring they all match
        probability = None  # Sentinel value
        for z_set in vertex_dcf:

            result = _marginalize_query(head, body, z_set)
            if probability is None:  # Storing first result
                probability = result

            # If results do NOT match; error
            assert abs(result-probability) < 0.00000001,  f"Error: Distinct results: {probability} vs {result}"

        logger.info(f"{0} = {1:.{5}f}".format(p_str(head, set(body) | set(interventions)), probability, precision=1))
        return result


def _marginalize_query(expression: Expression, deconfound: Collection[str], model: Model) -> float:
    """
    Handle the modified query where we require a deconfounding set due to Interventions / treatments.
    @param head: The head of the query, a set containing Outcome objects
    @param body: The body of the query, a set containing Outcome and Intervention objects
    @param dcf: A set of (string) names of variables to serve as a deconfounding set, blocking all backdoor paths
        between the head and body
    @return:
    """

    head = set(expression.head())
    body = set(expression.body())

    interventions = set(filter(lambda x: isinstance(x, Intervention), body))

    # Augment graph (isolating interventions as roots) and create engine
    model.graph().disable_incoming(*interventions)

    probability = 0.0

    # We take every possible combination of outcomes of Z and compute each probability separately
    for cross in product(*[model.variable(var).outcomes for var in deconfound]):

        # Construct the respective Outcome list of each Z outcome cross product
        z_outcomes = {Outcome(x, cross[i]) for i, x in enumerate(deconfound)}

        # First, we do P(Y | do(X), Z)
        logger.info(f"computing sub-query: {p_str(list(head), list(body | z_outcomes))}")
        p_y_x_z = inference(Expression(head, body | z_outcomes), model)

        # Second, P(Z)
        logger.info(f"computing sub-query: {p_str(list(z_outcomes), list(body))}")
        p_z = inference(Expression(z_outcomes, body), model)

        probability += p_y_x_z * p_z

    model.graph().reset_disabled()
    return probability
