#########################################################
#                                                       #
#   Do-Calculus Query Options                           #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Isolated for re-usability; let's take our graph, and our query, and return a list of
#   all possible applications of the do-calculus

from probability_structures.do_calculus.application.DoCalculusRules import *
from probability_structures.do_calculus.application.CustomSetFunctions import subtract, union
from probability_structures.Graph import Graph
from utilities.helpers.PowerSet import power_set


def do_calculus_options(query: QueryList, graph: Graph) -> list:
    """
    Take a QueryList and its Graph and see every valid rule that can be applied.
    :param query: The original QueryList
    :param graph: A graph to examine for paths, variables, etc.
    :return: A list of all possible actions to be done on the QueryList, where each item is a tuple
        (change message, resulting QueryList)
    """

    # Store a list of every possible "new" query resulting from a rule applied to this query
    all_results = []

    # Iterate through the entire query, seeing if any particular item can/needs to be simplified
    for item_index in range(len(query.queries)):

        # Can't do anything on Sigma
        if isinstance(query.queries[item_index], Sigma):
            continue

        # Find all possible options that can be applied to this specific query
        current_item = query.queries[item_index]
        specific_query_options = query_options(current_item, graph)

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


def query_options(query: Query, graph: Graph) -> list:
    """
    Take Query, and our Graph, and get a list of all valid options/results from Do-Calculus rule applications
    :param query: A Query instance
    :param graph: A graph consistent with the Query
    :return: A list of all possible actions to be done on the QueryList, where each item is a tuple
        (change message, resulting QueryList)
    """

    # Unpack the Variables of the given Query
    y, x, w = query.head, query.body.interventions, query.body.observations

    # Construct all possible sets by splitting interventions / observations
    # The following sets are tentative; not each subset will actually allow the rule to be applied until validated

    # First, all possible Z that can be deleted from our observations
    rule_1_tentative_z = union(set(power_set(w, False)), set(power_set(subtract(graph.v, (y | w | x)), False)))
    rule_1_valid_z = [set(s) for s in rule_1_tentative_z if rule_1_applicable(graph, y, x, set(s), w)]

    # Second, all possible Z that can switch between being observation/intervention
    rule_2_tentative_z = union(set(power_set(w, False)), set(power_set(x, False)))
    rule_2_valid_z = [set(s) for s in rule_2_tentative_z if rule_2_applicable(graph, y, x, set(s), w)]

    # Third, all possible Z that are subsets of our interventions that can be deleted
    rule_3_tentative_z = union(set(power_set(x, False)), set(power_set(subtract(graph.v, set(y | w | x)), False)))
    rule_3_valid_z = [set(s) for s in rule_3_tentative_z if rule_3_applicable(graph, y, x, set(s), w)]

    # Fourth, all possible Z that can be introduced by Jeffrey's Rule
    rule_4_tentative_z = set(power_set(subtract(graph.v, set(y | w | x | {"U"})), False))
    rule_4_valid_z = [set(s) for s in rule_4_tentative_z]

    # Present all options to the user (generating our menu as we go) and then get a selection
    do_options = []

    # All the steps of applying all 3 rules are the same (in terms of their arguments, creating strings to represent
    #   the results, etc. so this lets us take the addresses of each function rather than (pretty much) have 3 copied
    #   versions of the same code

    application = [{
        "rule": 1,
        "function": apply_rule_1,
        "verifier": rule_1_applicable,
        "sets": rule_1_valid_z,
        "check_subset": w,
        "subset_options": ["Delete Observation", "Insert Observation"]
    }, {
        "rule": 2,
        "function": apply_rule_2,
        "verifier": rule_2_applicable,
        "sets": rule_2_valid_z,
        "check_subset": x,
        "subset_options": ["Change to Observation", "Change to Intervention"]
    }, {
        "rule": 3,
        "function": apply_rule_3,
        "verifier": rule_3_applicable,
        "sets": rule_3_valid_z,
        "check_subset": x,
        "subset_options": ["Delete Intervention", "Insert Intervention"]
    }, {
        "rule": 4,
        "function": apply_secret_rule_4,
        "verifier": secret_rule_4_applicable,
        "sets": rule_4_valid_z,
    }]

    # Go through each rule, apply the rule to each of its applicable sets, and present the option
    for rule_application in application:

        # Create a skeleton of the message to allow it to be formatted depending on the subset checking
        rule = str(rule_application["rule"])
        query_message = "Rule " + rule + ": Making: {} -> {}."

        for z in rule_application["sets"]:

            # Apply the rule and get the result
            result = rule_application["function"](graph, y, x, z, w)

            # Verify that the rule still applies to "revert"; it always should.
            # error_skeleton = "Rule {} not found to be reversible! {} <-!-> {}, " \
            #                 "Y: {}, X: {}, Z: {}, W: {}, " \
            #                 "Y': {}, X': {}, Z': {}, W': {}, "
            # error_message = error_skeleton.format(rule, current_query, result_str,
            #                                      y, x, z, w,
            #                                      y_result, x_result, z, w_result)
            # try:
            #     assert rule_application["verifier"](graph, y_result, x_result, z, w_result), error_message
            # except AssertionError as e:
            #     print(e.args)

            # Generate the final "option" message and add it to the list of options
            # query = query_message.format(action, z_str, current_query, result_str)
            #do_options.append([CallableItemWrapper(y_result, x_result, w_result), query])
            if isinstance(result, tuple):
                new_message = " ".join(str(i) for i in result)
            else:
                new_message = str(result)

            do_options.append((query_message.format(str(query), new_message), result))

    return do_options
