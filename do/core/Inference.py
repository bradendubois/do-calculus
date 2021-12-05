from itertools import product
from loguru import logger
from typing import Collection, Union

from .Exceptions import ProbabilityException, ProbabilityIndeterminableException
from .Expression import Expression
from .Model import Model
from .Variables import Outcome, Intervention

from .helpers import p_str


def inference(expression: Expression, model: Model):

    def _compute(self, head: Collection[Outcome], body: Collection[Union[Outcome, Intervention]], depth=0) -> float:
        """
        Compute the probability of some head given some body
        @param head: A list of some number of Outcome objects
        @param body: A list of some number of Outcome objects
        @param depth: Used for horizontal offsets in outputting info
        @return: A probability between [0.0, 1.0]
        @raise ProbabilityIndeterminableException if the result cannot be computed for any reason
        """

        ###############################################
        #   Begin with bookkeeping / error-checking   #
        ###############################################

        # Sort the head and body if enabled
        # if Settings.topological_sort_variables:
        #     head, body = self.graph.descendant_first_sort(head), self.graph.descendant_first_sort(body)

        # Create a string representation of this query, and see if it's been done / in-progress / contradictory
        rep = p_str(head, body)

        logger.info(f"query: {rep}")

        # If the calculation has been done and cached, just return it from storage
        # if Settings.cache_computation_results and rep in self._stored_computations:
        #     result = self._stored_computations[rep]
        #     logger.info("Computation already calculated:", rep, "=", result, x=depth)
        #     return result

        # If the calculation for this contains two separate outcomes for a variable (Y = y | Y = ~y), 0
        if contradictory_outcome_set(head + body):
            logger.info(f"two separate outcomes for one variable, P = 0.0")
            return 0.0

        ###############################################
        #             Reverse product rule            #
        #   P(y, x | ~z) = P(y | x, ~z) * P(x | ~z)   #
        ###############################################

        if len(head) > 1:
            try:
                logger.info(f"applying reverse product rule to {rep}")

                result_1 = _compute(head[:-1], [head[-1]] + body, depth+1)
                result_2 = _compute([head[-1]], body, depth+1)
                result = result_1 * result_2

                logger.info(f"{rep} = {result}")
                # _store_computation(rep, result)
                return result

            except ProbabilityException:    # coverage: skip
                logger.info("Failed to resolve by reverse product rule.", x=depth)

        ###############################################
        #            Attempt direct lookup            #
        ###############################################

        if len(head) == 1 and model.graph().parents(head[0].name) == set(v.name for v in body):

            logger.info(f"querying table for: {rep}")
            table = model.tables[head[0].name]                           # Get table
            logger.info(f"{table}")                  # Show table
            probability = table.probability_lookup(head[0], body)       # Get specific row
            logger.info(f"{rep} = {probability}")

            return probability
        else:
            logger.info("no direct table found")

        ##################################################################
        #   Easy identity rule; P(X | X) = 1, so if LHS ⊆ RHS, P = 1.0   #
        ##################################################################

        if set(head).issubset(set(body)):
            logger.info(f"identity rule: X|X = 1.0, therefore {rep} = 1.0")
            return 1.0

        #################################################
        #                  Bayes' Rule                  #
        #     Detect children of the LHS in the RHS     #
        #      p(a|Cd) = p(d|aC) * p(a|C) / p(d|C)      #
        #################################################

        reachable_from_head = set().union(*[model.graph().descendants(outcome) for outcome in head])
        descendants_in_rhs = set([var.name for var in body]) & reachable_from_head

        if descendants_in_rhs:
            logger.info(f"Children of the LHS in the RHS: {','.join(descendants_in_rhs)}")
            logger.info("Applying Bayes' rule.")

            try:
                # Not elegant, but simply take one of the children from the body out and recurse
                child = list(descendants_in_rhs)[0]
                child = list(filter(lambda x: x.name == child, body))
                new_body = list(set(body) - set(child))

                str_1 = p_str(child, head + new_body)
                str_2 = p_str(head, new_body)
                str_3 = p_str(child, new_body)
                logger.info(f"{str_1} * {str_2} / {str_3}")

                result_1 = _compute(child, head + new_body, depth+1)
                result_2 = _compute(head, new_body, depth+1)
                result_3 = _compute(child, new_body, depth+1)
                if result_3 == 0:       # Avoid dividing by 0! coverage: skip
                    logger.info(f"{str_3} = 0, therefore the result is 0.")
                    return 0

                # flip flop flippy flop
                result = result_1 * result_2 / result_3
                logger.info(f"{rep} = {result}")
                # _store_computation(rep, result)
                return result

            except ProbabilityException:    # coverage: skip
                logger.info("Failed to resolve by Bayes")

        #######################################################################################################
        #                                  Jeffrey's Rule / Distributive Rule                                 #
        #   P(y | x) = P(y | z, x) * P(z | x) + P(y | ~z, x) * P(~z | x) === sigma_Z P(y | z, x) * P(z | x)   #
        #######################################################################################################

        missing_parents = set()
        for outcome in head:
            missing_parents.update(model.graph().parents(outcome) - set([parent.name for parent in head + body]))

        if missing_parents:
            logger.info("Attempting application of Jeffrey's Rule")

            for missing_parent in missing_parents:

                try:
                    # Add one parent back in and recurse
                    parent_outcomes = model.variable(missing_parent).outcomes

                    # Consider the missing parent and sum every probability involving it
                    total = 0.0
                    for parent_outcome in parent_outcomes:

                        as_outcome = Outcome(missing_parent, parent_outcome)

                        logger.info(p_str(head, [as_outcome] + body), "*", p_str([as_outcome], body), x=depth)

                        result_1 = _compute(head, [as_outcome] + body, depth+1)
                        result_2 = _compute([as_outcome], body, depth+1)
                        outcome_result = result_1 * result_2

                        total += outcome_result

                    logger.info(rep, "=", total, x=depth)
                    # _store_computation(rep, total)
                    return total

                except ProbabilityException:    # coverage: skip
                    logger.info("Failed to resolve by Jeffrey's Rule", x=depth)

        ###############################################
        #            Single element on LHS            #
        #               Drop non-parents              #
        ###############################################

        if len(head) == 1 and not missing_parents and not descendants_in_rhs:

            head_variable = head[0]
            can_drop = [v for v in body if v.name not in model.graph().parents(head_variable)]

            if can_drop:
                try:
                    logger.info("Can drop:", [str(item) for item in can_drop], x=depth)
                    result = _compute(head, list(set(body) - set(can_drop)), depth+1)
                    logger.info(rep, "=", str(result), x=depth)
                    # _store_computation(rep, result)
                    return result

                except ProbabilityException:    # coverage: skip
                    pass

        ###############################################
        #               Cannot compute                #
        ###############################################

        raise ProbabilityIndeterminableException    # coverage: skip

    head = set(expression.head())
    body = set(expression.body())

    for out in head | body:
        assert out.name in model.graph().v, f"Error: Unknown variable {out}"
        assert out.outcome in model.variable(out.name).outcomes[out.name], f"Error: Unknown outcome {out.outcome} for {out.name}"
        assert not isinstance(out, Intervention), f"Error: basic inference engine does not handle Interventions ({out.name} is an Intervention)"

    return _compute(list(head), list(body))


def contradictory_outcome_set(outcomes: Collection[Outcome]) -> bool:
    """
    Check whether a list of outcomes contain any contradictory values, such as Y = y and Y = ~y
    @param outcomes: A list of Outcome objects
    @return: True if there is a contradiction/implausibility, False otherwise
    """
    for x, y in product(outcomes, outcomes):
        if x.name == y.name and x.outcome != y.outcome:
            return True
    return False
