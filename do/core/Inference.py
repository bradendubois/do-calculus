from itertools import product
from loguru import logger
from typing import Collection

from .Exceptions import ExogenousNonRoot, ProbabilityIndeterminableException
from .Expression import Expression
from .Model import Model
from .Variables import Outcome, Intervention

from .helpers import within_precision


def inference(expression: Expression, model: Model):

    def _compute(head: Collection[Outcome], body: Collection[Intervention], depth=0) -> float:
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

        current_expression = Expression(head, body)
        logger.info(f"query: {current_expression}")

        # If the calculation for this contains two separate outcomes for a variable (Y = y | Y = ~y), 0
        if contradictory_outcome_set(head + body):
            logger.error("two separate outcomes for one variable, P = 0.0")
            return 0.0

        ###############################################
        #             Reverse product rule            #
        #   P(y, x | ~z) = P(y | x, ~z) * P(x | ~z)   #
        ###############################################

        if len(head) > 1:
            logger.info(f"applying reverse product rule to {current_expression}")

            result_1 = _compute(head[:-1], [head[-1]] + body, depth+1)
            result_2 = _compute([head[-1]], body, depth+1)
            result = result_1 * result_2

            logger.success(f"{current_expression} = {result}")
            return result

        ###############################################
        #            Attempt direct lookup            #
        ###############################################

        if set(model.variable(head[0].name).parents) == set(v.name for v in body):
            logger.info(f"querying table for: {current_expression}")
            table = model.table(head[0].name)                           # Get table
            probability = table.probability_lookup(head[0], body)       # Get specific row
            logger.success(f"{current_expression} = {probability}")

            return probability
        else:
            logger.info("no direct table found")

        ##################################################################
        #   Easy identity rule; P(X | X) = 1, so if LHS ⊆ RHS, P = 1.0   #
        ##################################################################

        if set(head).issubset(set(body)):
            logger.success(f"identity rule: X|X = 1.0, therefore {current_expression} = 1.0")
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

            # Not elegant, but simply take one of the children from the body out and recurse
            child = list(descendants_in_rhs)[0]
            child = list(filter(lambda x: x.name == child, body))
            new_body = list(set(body) - set(child))

            logger.info(f"{Expression(child, head + new_body)} * {Expression(head, new_body)} / {Expression(child, new_body)}")

            result_1 = _compute(child, head + new_body, depth+1)
            result_2 = _compute(head, new_body, depth+1)
            result_3 = _compute(child, new_body, depth+1)
            if result_3 == 0:       # Avoid dividing by 0! coverage: skip
                logger.success(f"{Expression([child], new_body)} = 0, therefore the result is 0.")
                return 0

            # flip flop flippy flop
            result = result_1 * result_2 / result_3
            logger.success(f"{current_expression} = {result}")
            return result

        #######################################################################################################
        #                                  Jeffrey's Rule / Distributive Rule                                 #
        #   P(y | x) = P(y | z, x) * P(z | x) + P(y | ~z, x) * P(~z | x) === sigma_Z P(y | z, x) * P(z | x)   #
        #######################################################################################################

        missing_parents = set()
        for outcome in head:
            missing_parents.update(set(model.variable(outcome.name).parents) - set([parent.name for parent in head + body]))

        if missing_parents:
            logger.info("Attempting application of Jeffrey's Rule")

            for missing_parent in missing_parents:

                # Add one parent back in and recurse
                parent_outcomes = model.variable(missing_parent).outcomes

                # Consider the missing parent and sum every probability involving it
                total = 0.0
                for parent_outcome in parent_outcomes:

                    as_outcome = Outcome(missing_parent, parent_outcome)

                    logger.info(f"{Expression(head, [as_outcome] + body)}, * {Expression([as_outcome], body)}")

                    result_1 = _compute(head, [as_outcome] + body, depth+1)
                    result_2 = _compute([as_outcome], body, depth+1)
                    outcome_result = result_1 * result_2

                    total += outcome_result

                logger.success(f"{current_expression} = {total}")
                return total

        ###############################################
        #            Single element on LHS            #
        #               Drop non-parents              #
        ###############################################

        if len(head) == 1 and not missing_parents and not descendants_in_rhs:

            head_variable = head[0].name
            can_drop = [v for v in body if v.name not in model.variable(head_variable).parents]

            if can_drop:
                logger.info(f"can drop: {[str(item) for item in can_drop]}")
                result = _compute(head, list(set(body) - set(can_drop)), depth+1)
                logger.success(f"{current_expression} = {result}")
                return result

        ###############################################
        #               Cannot compute                #
        ###############################################

        raise ProbabilityIndeterminableException

    head = set(expression.head())
    body = set(expression.body())

    for out in head | body:
        assert out.name in model.graph().v, f"Error: Unknown variable {out}"
        assert out.outcome in model.variable(out.name).outcomes, f"Error: Unknown outcome {out.outcome} for {out.name}"
        assert not isinstance(out, Intervention), \
            f"Error: basic inference engine does not handle Interventions ({out.name} is an Intervention)"

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


def validate(model: Model) -> bool:
    """
    Ensures a model is 'valid' and 'consistent'.
    1. Ensures the is a DAG (contains no cycles)
    2. Ensures all variables denoted as exogenous are roots.
    3. Ensures all distributions are consistent (the sum of probability of each outcome is 1.0)

    Returns True on success (indicating a valid model), or raises an appropriate Exception indicating a failure.
    """
    # no cycles
    ...

    # exogenous variables are all roots
    exogenous = model._g.v - set(model._v.keys())
    roots = model._g.roots()
    for variable in exogenous:
        if variable not in roots:
            raise ExogenousNonRoot(variable)

    # consistent distributions
    for name, variable in model._v.items():
        t = 0
        for outcome in variable.outcomes:
            t += inference(Expression(Outcome(name, outcome)), model)

        assert within_precision(t, 1)

    # all checks passed -> valid model
    return True
