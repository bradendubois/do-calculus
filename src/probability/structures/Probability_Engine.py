#########################################################
#                                                       #
#   IDS Queue                                           #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Here we can isolate the probability computations involved in something like P(Y | X)

import itertools

from src.probability.structures.Graph import Graph
from src.probability.structures.VariableStructures import *

from src.util.IO_Logger import io
from src.util.parsers.ProbabilityString import p_str
from src.util.ResultCache import *
from src.util.ProbabilityExceptions import *


class ProbabilityEngine:

    error_msg_formatting = \
        "The given data is incorrect:\n" + \
        " - Some outcome may not be possible for some variable\n" + \
        " - Some variable may not be defined"

    def __init__(self, graph: Graph, outcomes: dict, tables: dict):
        """
        The basics required to create the probability engine
        :param graph: A Graph to be traversed in making these computations
        :param outcomes: A dictionary mapping of variable to its respective outcomes
        :param tables: A dictionary mapping of Variable to its lookup table
        """
        self.graph = graph.copy()
        self.outcomes = outcomes
        self.tables = tables

    def probability(self, query: str or list or (list, list)) -> float:
        """
        The public-facing probability function
        :param query: either something like "X=x | Y=y" or 1-2 lists representing the head, and then body, as Outcomes
        :return: A specific probability in [0.0, 1.0]
        """
        if isinstance(query, tuple):
            head, body = query
        elif isinstance(query, list):
            head, body = query, []
        elif isinstance(query, str):
            if "|" in query:
                head_string, body_string = query.split("|")
            else:
                head_string, body_string = query, ""

            assert head_string != "", "No query being made: the head should not be empty"
            head, body = parse_outcomes_and_interventions(head_string), parse_outcomes_and_interventions(body_string)
        else:
            print("Confusing query parameter type: " + str(type(query)))
            if isinstance(query, tuple):
                print("Tuple of: " + ", ".join([str(type(i)) for i in query]))
            raise Exception

        # Ensure there are no adjustments/interventions in the head
        for out in head:
            assert not isinstance(out, Intervention), "Don't put adjustments in the head."

        # Validate the queried variables and any given
        # Ensure variable is defined, outcome is possible for that variable, and it's formatted right.
        for out in list(head) + list(body):
            assert out.name in self.graph.v and out.outcome in self.outcomes[out.name], self.error_msg_formatting

        # Double check that all our edges are properly disabled where they should be
        self.graph.reset_disabled()
        self.graph.disable_incoming(*{s for s in list(head) + list(body) if isinstance(s, Intervention)})
        return self._compute(head, body)

    def _compute(self, head: list, body: list, depth=0) -> float:
        """
        Compute the probability of some head given some body
        :param head: A list of some number of Outcome objects
        :param body: A list of some number of Outcome objects
        :param depth: Used for horizontal offsets in outputting info
        :return: A probability between [0.0, 1.0]
        """

        ###############################################
        #   Begin with bookkeeping / error-checking   #
        ###############################################

        # Sort the head and body if enabled
        if access("topological_sort_variables"):
            head, body = self.graph.descendant_first_sort(head), self.graph.descendant_first_sort(body)

        # Create a string representation of this query, and see if it's been done / in-progress / contradictory
        str_rep = p_str(head, body)

        # Print the actual query being made on each recursive call to help follow
        io.write_log("Querying:", str_rep, x_offset=depth)

        # If the calculation has been done and cached, just return it from storage
        if str_rep in stored_computations:
            result = stored_computations[str_rep]
            io.write_log("Computation already calculated:", str_rep, "=", result, x_offset=depth)
            return result

        # If the calculation for this contains two separate outcomes for a variable (Y = y | Y = ~y), 0
        if self.contradictory_outcome_set(head + body):
            io.write_log("Two separate outcomes for one variable: 0.0")
            return 0.0

        ###############################################
        #             Reverse product rule            #
        #   P(y, x | ~z) = P(y | x, ~z) * P(x | ~z)   #
        ###############################################

        if len(head) > 1:
            try:
                io.write_log("Applying reverse product rule to", str_rep, x_offset=depth)

                result_1 = self._compute(head[:-1], [head[-1]] + body, depth+1)
                result_2 = self._compute([head[-1]], body, depth+1)
                result = result_1 * result_2

                io.write_log(str_rep, "=", str(result), x_offset=depth)
                store_computation(str_rep, result)
                return result
            except ProbabilityException:
                io.write_log("Failed to resolve by reverse product rule.", x_offset=depth)

        ###############################################
        #            Attempt direct lookup            #
        ###############################################

        if len(head) == 1 and set(self.tables[head[0].name].given) == set(v.name for v in body):

            io.write_log("Querying table for: ", p_str(head, body), x_offset=depth, end="")
            table = self.tables[head[0].name]                       # Get table
            io.write_log(str(table), x_offset=depth, end="")            # Show table
            probability = table.probability_lookup(head, body)      # Get specific row
            io.write_log(p_str(head, body), "=", probability, x_offset=depth)

            return probability
        else:
            io.write_log("No direct table found.", x_offset=depth)

        ##################################################################
        #   Easy identity rule; P(X | X) = 1, so if LHS ⊆ RHS, P = 1.0   #
        ##################################################################

        if set(head).issubset(set(body)):
            io.write_log("Identity rule:", p_str(head, head), " = 1.0", x_offset=depth)
            if len(head) > len(body):
                io.write_log("Therefore,", p_str(head, body), "= 1.0", x_offset=depth)
            return 1.0

        #################################################
        #                  Bayes' Rule                  #
        #     Detect children of the LHS in the RHS     #
        #      p(a|Cd) = p(d|aC) * p(a|C) / p(d|C)      #
        #################################################

        reachable_from_head = set().union(*[self.graph.reach(outcome) for outcome in head])
        descendants_in_rhs = set([var.name for var in body]) & reachable_from_head

        if descendants_in_rhs:
            io.write_log("Children of the LHS in the RHS:", ",".join(descendants_in_rhs), x_offset=depth, end="")
            io.write_log("Applying Bayes' rule.", x_offset=depth)

            try:
                # Not elegant, but simply take one of the children from the body out and recurse
                child = list(descendants_in_rhs).pop(0)
                child = [item for item in body if item.name == child]
                new_body = list(set(body) - set(child))

                str_1 = p_str(child, head + new_body)
                str_2 = p_str(head, new_body)
                str_3 = p_str(child, new_body)
                io.write_log(str_1, "*", str_2, "/", str_3, x_offset=depth)

                result_1 = self._compute(child, head + new_body, depth+1)
                result_2 = self._compute(head, new_body, depth+1)
                result_3 = self._compute(child, new_body, depth+1)
                if result_3 == 0:       # Avoid dividing by 0!
                    io.write_log(str_3, "= 0, therefore the result is 0.", x_offset=depth)
                    return 0

                # flip flop flippy flop
                result = result_1 * result_2 / result_3
                io.write_log(str_rep, "=", str(result), x_offset=depth)
                store_computation(str_rep, result)
                return result

            except ProbabilityException:
                io.write_log("Failed to resolve by Bayes", x_offset=depth)

        #######################################################################################################
        #                                  Jeffrey's Rule / Distributive Rule                                 #
        #   P(y | x) = P(y | z, x) * P(z | x) + P(y | ~z, x) * P(~z | x) === sigma_Z P(y | z, x) * P(z | x)   #
        #######################################################################################################

        missing_parents = set()
        for outcome in head:
            missing_parents.update(self.graph.parents(outcome) - set([parent.name for parent in head + body]))

        if missing_parents:
            io.write_log("Attempting application of Jeffrey's Rule", x_offset=depth)

            # Try an approach beginning with each missing parent
            for missing_parent in missing_parents:

                try:
                    # Add one parent back in and recurse
                    parent_outcomes = self.outcomes[missing_parent]

                    # Consider the missing parent and sum every probability involving it
                    total = 0.0
                    for parent_outcome in parent_outcomes:

                        as_outcome = Outcome(missing_parent, parent_outcome)

                        io.write_log(p_str(head, [as_outcome] + body), "*", p_str([as_outcome], body), x_offset=depth)

                        result_1 = self._compute(head, [as_outcome] + body, depth+1)
                        result_2 = self._compute([as_outcome], body, depth+1)
                        outcome_result = result_1 * result_2

                        total += outcome_result

                    io.write_log(str_rep, "=", str(total), x_offset=depth)
                    store_computation(str_rep, total)
                    return total

                except ProbabilityException:
                    io.write_log("Failed to resolve by Jeffrey's Rule", x_offset=depth)

        ###############################################
        #            Interventions / do(X)            #
        ###############################################

        # Interventions imply that we have fixed X=x
        if isinstance(head[0], Intervention) and len(head) == 1 and not descendants_in_rhs:
            io.write_log("Intervention without RHS Children:", str_rep, "= 1.0", x_offset=depth)
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
                    io.write_log("Can drop:", str([str(item) for item in can_drop]), x_offset=depth)
                    result = self._compute(head, list(set(body) - set(can_drop)), depth+1)
                    io.write_log(str_rep, "=", str(result), x_offset=depth)
                    store_computation(str_rep, result)
                    return result

                except ProbabilityException:
                    pass

        ###############################################
        #               Cannot compute                #
        ###############################################

        raise ProbabilityIndeterminableException

    def contradictory_outcome_set(self, outcomes: list) -> bool:
        """
        Check whether a list of outcomes contain any contradictory values, such as Y = y and Y = ~y
        :param outcomes: A list of Outcome objects
        :return: True if there is a contradiction/implausibility, False otherwise
        """
        for cross in itertools.product(outcomes, outcomes):
            if cross[0].name == cross[1].name and cross[0].outcome != cross[1].outcome:
                return True
        return False
