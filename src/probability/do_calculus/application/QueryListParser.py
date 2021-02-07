#########################################################
#                                                       #
#   QueryList Parser                                   #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Take a QueryList and evaluate the probability (assumes a valid/correct QueryList)

from itertools import product

from src.probability.do_calculus.application.CustomSetFunctions import clean
from src.probability.do_calculus.application.QueryStructures import QueryList, Sigma, Query
from src.probability.structures.Graph import Graph, Outcome, Intervention
from src.probability.structures.Probability_Engine import ProbabilityEngine


def ql_probability(known: dict, graph: Graph, outcomes: dict, tables: dict, ql: QueryList, **kwargs):
    """
    Take a QueryList and return its evaluated probability
    :param known: A dictionary mapping a variable (which may be renamed) to its current value
    :param graph: A graph to consult in computing the probabilities involved
    :param outcomes: A dictionary mapping a variable to its list of possible outcomes
    :param tables: A dictionary mapping a variable to its conditional probability table
    :param ql: A QueryList object
    :param kwargs: keyword arguments, allowing a parsed graph file to be unpacked into a ql_probability call, such as
        (where "parsed" is a dictionary representing the parsed contents) ql_probability(**parsed)
    :return: A probability, between [0.0, 1.0] representing the final probability of this query
    """

    # Copy the QueryList, pop the front off for processing
    new_ql = ql.copy()
    item = new_ql.queries.pop(0)

    # Sigma symbol, sum over every value in the set
    if isinstance(item, Sigma):

        # Sum over every cross product of all these outcomes
        total = 0
        over = list(item.over)

        # Cross product of all the possible outcomes
        for cross in product(*[outcomes[clean(v)] for v in over]):

            # Copy the dictionary mapping variables to rename
            new_known = known.copy()

            # Save this exact combination of variable->value maps
            set_values = [(v, cross[i]) for i, v in enumerate(over)]
            for value in set_values:
                new_known[value[0]] = value[1]

            # Add <whatever the rest of this query works out to> to our total
            total += ql_probability(new_known, graph, outcomes, tables, new_ql)

        # Return the total
        return total

    # Query, compute it given what we currently know
    else:

        # Help the linter with some type hinting
        item: Query

        # Can simply convert everything in our head to Outcomes - shouldn't contain any Interventions
        head = {Outcome(clean(variable), known[variable]) for variable in item.head}

        # Convert everything in the body to either an Outcome or Intervention, "cleaning" the variable name so that
        #   all variables are consistent with the graph
        body_interventions = {Intervention(clean(variable), known[variable]) for variable in item.body.interventions}
        body_outcomes = {Outcome(clean(variable), known[variable]) for variable in item.body.observations}

        # Resulting probability this Query item
        result = ProbabilityEngine(graph, outcomes, tables).probability(head, body_outcomes | body_interventions)

        # All done
        if len(new_ql.queries) == 0:
            return result

        # The QueryList isn't complete, multiply this probability against <whatever the rest evaluates to>
        return result * ql_probability(known, graph, outcomes, tables, new_ql)

