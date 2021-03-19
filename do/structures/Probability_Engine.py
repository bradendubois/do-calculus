#########################################################
#                                                       #
#   Probability Engine                                  #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

from itertools import product
from typing import Collection, Union

from .Graph import Graph
from .VariableStructures import Outcome, Intervention

from ..config.settings import Settings
from ..util.OutputLogger import OutputLogger
from ..util.helpers import p_str
from ..util.ProbabilityExceptions import ProbabilityException, ProbabilityIndeterminableException


class ProbabilityEngine:

    def __init__(self, graph: Graph, outcomes: dict, tables: dict, **kwargs):
        """
        The basics required to create the probability engine
        @param graph: A Graph to be traversed in making these computations
        @param outcomes: A dictionary mapping of variable to its respective outcomes
        @param tables: A dictionary mapping of Variable to its lookup table
        """
        self.graph = graph.copy()
        self.outcomes = outcomes
        self.tables = tables
        self.output = kwargs["output"] if "output" in kwargs else OutputLogger()
        self._stored_computations = dict()

    def probability(self, head: Collection[Outcome], body: Collection[Union[Outcome, Intervention]]) -> float:
        """
        @param head: A set of Outcome objects representing the head of a query
        @param body: A set of Outcome/Intervention objects representing the body of a query
        @return: A probability in the range [0.0, 1.0], if it can be computed
        @raise AssertionError if an Outcome/Intervention provided is not defined in the given model
        @raise AssertionError if there is an Intervention in the head
        """

        head = set(head)
        body = set(body)

        # Ensure there are no adjustments/interventions in the head
        for out in head:
            assert not isinstance(out, Intervention), f"Error: {out} is in head; no Interventions should be in head."

        # Validate the queried variables and any given
        # Ensure variable is defined, outcome is possible for that variable, and it's formatted right.
        for out in head | body:
            assert out.name in self.graph.v, f"Error: Unknown variable {out}"
            assert out.outcome in self.outcomes[out.name], f"Error: Unknown outcome {out.outcome} for {out.name}"

        interventions = list(filter(lambda x: isinstance(x, Intervention), body))

        # Double check that all our edges are properly disabled where they should be
        self.graph.reset_disabled()
        self.graph.disable_incoming(*interventions)
        return self._compute(list(head), list(body))

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
        if Settings.topological_sort_variables:
            head, body = self.graph.descendant_first_sort(head), self.graph.descendant_first_sort(body)

        # Create a string representation of this query, and see if it's been done / in-progress / contradictory
        rep = p_str(head, body)

        # Print the actual query being made on each recursive call to help follow
        self.output.detail("Querying:", rep, x=depth)

        # If the calculation has been done and cached, just return it from storage
        if rep in self._stored_computations:
            result = self._stored_computations[rep]
            self.output.detail("Computation already calculated:", rep, "=", result, x=depth)
            return result

        # If the calculation for this contains two separate outcomes for a variable (Y = y | Y = ~y), 0
        if contradictory_outcome_set(head + body):
            self.output.detail("Two separate outcomes for one variable: 0.0")
            return 0.0

        ###############################################
        #             Reverse product rule            #
        #   P(y, x | ~z) = P(y | x, ~z) * P(x | ~z)   #
        ###############################################

        if len(head) > 1:
            try:
                self.output.detail("Applying reverse product rule to", rep, x=depth)

                result_1 = self._compute(head[:-1], [head[-1]] + body, depth+1)
                result_2 = self._compute([head[-1]], body, depth+1)
                result = result_1 * result_2

                self.output.detail(rep, "=", result, x=depth)
                self._store_computation(rep, result)
                return result
            except ProbabilityException:    # coverage: skip
                self.output.detail("Failed to resolve by reverse product rule.", x=depth)

        ###############################################
        #            Attempt direct lookup            #
        ###############################################

        if len(head) == 1 and self.graph.parents(head[0].name) == set(v.name for v in body):

            self.output.detail(f"Querying table for: {rep}", x=depth, end="")
            table = self.tables[head[0].name]                           # Get table
            self.output.detail(table, x=depth, end="")                  # Show table
            probability = table.probability_lookup(head[0], body)       # Get specific row
            self.output.detail(rep, "=", probability, x=depth)

            return probability
        else:
            self.output.detail("No direct table found.", x=depth)

        ##################################################################
        #   Easy identity rule; P(X | X) = 1, so if LHS ⊆ RHS, P = 1.0   #
        ##################################################################

        if set(head).issubset(set(body)):
            self.output.detail(f"Identity rule: X|X, therefore {rep} = 1.0", x=depth)
            return 1.0

        #################################################
        #                  Bayes' Rule                  #
        #     Detect children of the LHS in the RHS     #
        #      p(a|Cd) = p(d|aC) * p(a|C) / p(d|C)      #
        #################################################

        reachable_from_head = set().union(*[self.graph.reach(outcome) for outcome in head])
        descendants_in_rhs = set([var.name for var in body]) & reachable_from_head

        if descendants_in_rhs:
            self.output.detail(f"Children of the LHS in the RHS: {','.join(descendants_in_rhs)}", x=depth, end="")
            self.output.detail("Applying Bayes' rule.", x=depth)

            try:
                # Not elegant, but simply take one of the children from the body out and recurse
                child = list(descendants_in_rhs)[0]
                child = list(filter(lambda x: x.name == child, body))
                new_body = list(set(body) - set(child))

                str_1 = p_str(child, head + new_body)
                str_2 = p_str(head, new_body)
                str_3 = p_str(child, new_body)
                self.output.detail(f"{str_1} * {str_2} / {str_3}", x=depth)

                result_1 = self._compute(child, head + new_body, depth+1)
                result_2 = self._compute(head, new_body, depth+1)
                result_3 = self._compute(child, new_body, depth+1)
                if result_3 == 0:       # Avoid dividing by 0! coverage: skip
                    self.output.detail(f"{str_3} = 0, therefore the result is 0.", x=depth)
                    return 0

                # flip flop flippy flop
                result = result_1 * result_2 / result_3
                self.output.detail(f"{rep} = {result}", x=depth)
                self._store_computation(rep, result)
                return result

            except ProbabilityException:    # coverage: skip
                self.output.detail("Failed to resolve by Bayes", x=depth)

        #######################################################################################################
        #                                  Jeffrey's Rule / Distributive Rule                                 #
        #   P(y | x) = P(y | z, x) * P(z | x) + P(y | ~z, x) * P(~z | x) === sigma_Z P(y | z, x) * P(z | x)   #
        #######################################################################################################

        missing_parents = set()
        for outcome in head:
            missing_parents.update(self.graph.parents(outcome) - set([parent.name for parent in head + body]))

        if missing_parents:
            self.output.detail("Attempting application of Jeffrey's Rule", x=depth)

        for missing_parent in missing_parents:

            try:
                # Add one parent back in and recurse
                parent_outcomes = self.outcomes[missing_parent]

                # Consider the missing parent and sum every probability involving it
                total = 0.0
                for parent_outcome in parent_outcomes:

                    as_outcome = Outcome(missing_parent, parent_outcome)

                    self.output.detail(p_str(head, [as_outcome] + body), "*", p_str([as_outcome], body), x=depth)

                    result_1 = self._compute(head, [as_outcome] + body, depth+1)
                    result_2 = self._compute([as_outcome], body, depth+1)
                    outcome_result = result_1 * result_2

                    total += outcome_result

                self.output.detail(rep, "=", total, x=depth)
                self._store_computation(rep, total)
                return total

            except ProbabilityException:    # coverage: skip
                self.output.detail("Failed to resolve by Jeffrey's Rule", x=depth)

        ###############################################
        #            Interventions / do(X)            #
        ###############################################

        # Interventions imply that we have fixed X=x
        if isinstance(head[0], Intervention) and len(head) == 1 and not descendants_in_rhs:
            self.output.detail("Intervention without RHS Children:", rep, "= 1.0", x=depth)
            return 1.0

        ###############################################
        #            Single element on LHS            #
        #               Drop non-parents              #
        ###############################################

        if len(head) == 1 and not missing_parents and not descendants_in_rhs:

            head_variable = head[0]
            can_drop = [v for v in body if v.name not in self.graph.parents(head_variable)]

            if can_drop:
                try:
                    self.output.detail("Can drop:", [str(item) for item in can_drop], x=depth)
                    result = self._compute(head, list(set(body) - set(can_drop)), depth+1)
                    self.output.detail(rep, "=", str(result), x=depth)
                    self._store_computation(rep, result)
                    return result

                except ProbabilityException:    # coverage: skip
                    pass

        ###############################################
        #               Cannot compute                #
        ###############################################

        raise ProbabilityIndeterminableException    # coverage: skip

    def _store_computation(self, string_representation: str, result: float):
        """
        Store a computed result mapped by its query/representation, to speed up future queries
        @param string_representation: Whatever representation for this query: "P(Y | X)", etc.
        @param result: The actual float value to store
        """
        # Ensure the configuration file is specified to allow caching
        if Settings.cache_computation_results:

            # Not stored yet - store it
            if string_representation not in self._stored_computations:
                self._stored_computations[string_representation] = result

            # Stored already but with a different value - something fishy is going on...
            elif self._stored_computations[string_representation] != result:    # coverage: skip
                print("Uh-oh:", string_representation, "has already been cached, but with a different value...")


def contradictory_outcome_set(outcomes: Collection[Union[Outcome, Intervention]]) -> bool:
    """
    Check whether a list of outcomes contain any contradictory values, such as Y = y and Y = ~y
    @param outcomes: A list of Outcome objects
    @return: True if there is a contradiction/implausibility, False otherwise
    """
    for x, y in product(outcomes, outcomes):
        if x.name == y.name and x.outcome != y.outcome:
            return True
    return False
