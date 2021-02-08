#########################################################
#                                                       #
#   Do-Calculus Query Options                           #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Isolated for re-usability; let's take our graph, and our query, and return a list of
#   all possible applications of the do-calculus or standard inference rules

from src.probability.do_calculus.application.rules.DoCalculusRules import *
from src.probability.do_calculus.application.rules.StandardInferenceRules import *
from src.probability.do_calculus.application.CustomSetFunctions import subtract, union
from src.probability.do_calculus.application.QueryStructures import QueryList
from src.probability.structures.Graph import Graph

from src.util.helpers import power_set

# A dictionary cache to store already-computed Query results rather than constantly recompute them from scratch
query_cache = dict()


def do_calculus_options(query: QueryList, graph: Graph, u: set) -> list:
    """
    Take a QueryList and its Graph and see every valid rule that can be applied.
    :param query: The original QueryList
    :param graph: A graph to examine for paths, variables, etc.
    :param u: A set of unobservable variables
    :return: A list of all possible actions to be done on the QueryList, where each item is a tuple
        (change message, resulting QueryList)
    """

    # Store a list of every possible "new" query resulting from a rule applied to this query
    all_results = []

    # Iterate through the entire query, seeing if any particular item can/needs to be simplified
    for item_index in range(len(query.queries)):

        current_item: Sigma or Query
        current_item = query.queries[item_index]

        # Can't do anything on Sigma
        if isinstance(current_item, Sigma):
            continue

        # Don't need to do anything on a resolved subquery
        if current_item.resolved():
            continue

        # Already computed this before, results are cached
        if str(current_item) in query_cache:
            specific_query_options = query_cache[str(current_item)]

        # Find all possible options that can be applied to this specific query
        else:
            specific_query_options = query_options(current_item, graph, u)
            query_cache[str(current_item)] = specific_query_options

        # Take a copy of the current state of the query, applying each possible rule
        for option in specific_query_options:

            # Unpack this specific option
            message, result = option

            # Copy the current query
            new_query = query.copy()

            # Handle how to unpack the option, since we return 1 item or a tuple of items
            if isinstance(result, tuple):
                unpacked = [*result]
            else:
                unpacked = [result]

            # Apply the option/rule
            new_query.queries[item_index:item_index+1] = unpacked

            # Add this viable "path" to the list of options
            all_results.append((message, new_query))

    return all_results


def query_options(query: Query, graph: Graph, u: set) -> list:
    """
    Take Query, and our Graph, and get a list of all valid options/results from Do-Calculus rule applications
    :param query: A Query instance
    :param graph: A graph consistent with the Query
    :param u: A set of unobservable variables
    :return: A list of all possible actions to be done on the QueryList, where each item is a tuple
        (change message, resulting QueryList)
    """

    # Unpack the Variables of the given Query
    y, x, w = query.head, query.body.interventions, query.body.observations

    # Construct all possible sets by splitting interventions / observations
    # The following sets are tentative; not each subset will actually allow the rule to be applied until validated

    # First, all possible Z that can be deleted from our observations
    rule_1_tentative_z = union(set(power_set(w, False)), set(power_set(subtract(graph.v, (y | w | x | u)), False)))
    # rule_1_tentative_z = union(set(power_set(w, False)), set(power_set(subtract(graph.v, (y | w | x)), False)))
    rule_1_valid_z = [set(s) for s in rule_1_tentative_z if rule_1_applicable(graph, y, x, set(s), w)]

    # Second, all possible Z that can switch between being observation/intervention
    rule_2_tentative_z = union(set(power_set(w, False)), set(power_set(x, False)))
    rule_2_valid_z = [set(s) for s in rule_2_tentative_z if rule_2_applicable(graph, y, x, set(s), w)]

    # Third, all possible Z that are subsets of our interventions that can be deleted
    rule_3_tentative_z = union(set(power_set(x, False)), set(power_set(subtract(graph.v, set(y | w | x | u)), False)))
    # rule_3_tentative_z = union(set(power_set(x, False)), set(power_set(subtract(graph.v, set(y | w | x)), False)))
    rule_3_valid_z = [set(s) for s in rule_3_tentative_z if rule_3_applicable(graph, y, x, set(s), w)]

    # Fourth, all possible Z that can be introduced by Jeffrey's Rule
    condition_z = set(power_set(subtract(graph.v, set(y | w | x | u)), False))
    # condition_z = set(power_set(subtract(graph.v, set(y | w | x)), False))

    # Fifth, any possible sets of Y that are greater than 1, and not the entire set
    product_rule_z = [set(s) for s in set(power_set(y, False)) if 1 <= len(s) < len(y)]

    # Test - filter to only move one variable at a time
    # rule_1_valid_z = [s for s in rule_1_valid_z if len(s) == 1]
    # rule_2_valid_z = [s for s in rule_2_valid_z if len(s) == 1]
    # rule_3_valid_z = [s for s in rule_3_valid_z if len(s) == 1]
    # condition_z = [s for s in condition_z if len(s) == 1]
    # product_rule_z = [s for s in product_rule_z if len(s) == 1]

    # Present all options to the user (generating our menu as we go) and then get a selection
    do_options = []

    # Each rule, the function that should be called, and the sets that will serve as our "Z".
    application = [{
        "rule": 1,
        "function": apply_rule_1,
        "sets": rule_1_valid_z,
    }, {
        "rule": 2,
        "function": apply_rule_2,
        "sets": rule_2_valid_z,
    }, {
        "rule": 3,
        "function": apply_rule_3,
        "sets": rule_3_valid_z,
    }, {
        "rule": "Conditioning",
        "function": condition,
        "sets": condition_z,
    }, {
        "rule": "Product Rule",
        "function": apply_product_rule,
        "sets": product_rule_z
    }]

    # Go through each rule, apply the rule to each of its applicable sets, and present the option
    for rule_application in application:

        # Create a skeleton of the message to allow it to be formatted depending on the subset checking
        rule = str(rule_application["rule"])
        query_message = "Rule " + rule + ": Making: {} -> {}."

        for z in rule_application["sets"]:

            # Apply the rule and get the result
            result = rule_application["function"](graph, y, x, z, w)

            # Introduced a Sigma Query Query tuple
            if isinstance(result, tuple):
                new_message = " ".join(str(i) for i in result)
            # Single Query
            else:
                new_message = str(result)

            # Push the option to the list
            do_options.append((query_message.format(str(query), new_message), result))

    return do_options
