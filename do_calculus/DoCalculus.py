#########################################################
#                                                       #
#   Do Calculus                                         #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Determine if any of the 3 rules of do_calculus can be applied to a given graph and query

from probability_structures.BackdoorController import BackdoorController
from probability_structures.Graph import Graph

from utilities.IO_Logger import io
from utilities.helpers.PowerSet import power_set
from utilities.parsing.UserIndexSelection import user_index_selection


class ResultWrapper:
    """Helper class to allow data to be passed through my menu / io system without errors by being "callable" """

    def __init__(self, *data):
        self.data = data

    # My menu system has behaviour defined by "callable" data, so this is a bit of a workaround.
    def __call__(self, *args, **kwargs):
        pass


#################################################
#   Rule 1 - Insertion/deletion of observation  #
#################################################

def rule_1_applicable(graph: Graph, y: set, x: set, z: set, w: set) -> bool:

    # Disable the incoming X edges
    graph.reset_disabled()
    graph.disable_incoming(*x)

    # See if Y _||_ Z
    independent = BackdoorController(graph).independent(y, z, x | w)
    # print(str(y), str(x), str(z), str(w), independent)

    return independent


def apply_rule_1(graph: Graph, y: set, x: set, z: set, w: set):

    # Double check
    assert rule_1_applicable(graph, y, x, z, w), "Rule 1 not applicable!"

    # Deleting Z from W if it's already in W
    if z.issubset(w):
        return y, x, w - z

    # Not in W - inserting Z
    else:
        return y, x, w | z


###################################################
#   Rule 2 - Action/observation exchange          #
###################################################

def rule_2_applicable(graph: Graph, y: set, x: set, z: set, w: set):

    # Disable incoming X edges, outgoing Z edges
    graph.reset_disabled()
    graph.disable_incoming(*x)
    graph.disable_outgoing(*z)

    # See if Y _||_ Z
    independent = BackdoorController(graph).independent(y, z, x | w)
    # print(str(y), str(x), str(z), str(w), independent)

    return independent


def apply_rule_2(graph: Graph, y: set, x: set, z: set, w: set):

    # Double check
    assert rule_2_applicable(graph, y, x, z, w), "Rule 2 is not applicable!"

    # Dropping z from Interventions X if that is where it currently is
    if z.issubset(x):
        return y, x - z, w | z

    # Dropping it from our Observations
    else:
        return y, x | z, w - z


###################################################
#   Rule 3 - Insertion/deletion of actions        #
###################################################

def rule_3_applicable(graph: Graph, y: set, x: set, z: set, w: set):

    # Disable X incoming edges, all edges incoming to any non-ancestor of any W node in G ^X
    graph.reset_disabled()
    graph.disable_incoming(*x)
    all_w_ancestors = set().union(*[graph.full_ancestors(v) for v in w])
    zw = z - all_w_ancestors
    graph.disable_incoming(*zw)

    # See if Y _||_ Z
    independent = BackdoorController(graph).independent(y, z, x | w)
    # print(str(y), str(x), str(z), str(w), independent)

    return independent


def apply_rule_3(graph: Graph, y: set, x: set, z: set, w: set):

    assert rule_3_applicable(graph, y, x, z, w), "Rule 3 is not applicable!"

    if z.issubset(x):
        return y, x - z, w
    else:
        return y, x | z, w


##############
#   Helper   #
##############

def query_str(y, interventions, observations, z=None, z_is_intervention=False):

    # TODO - Reformat as the RHS being a list of each set-string, joined by commas

    lhs = ",".join(y)
    rhs = ""
    if len(interventions) > 0:
        rhs += "do(" + ",".join(interventions) + ")"
    if len(interventions) > 0 and (z or len(observations) > 0):
        rhs += ", "
    if z:
        if z_is_intervention:
            rhs += "do("
        rhs += ",".join(z)
        if z_is_intervention:
            rhs += ")"
    if z and len(observations) > 0:
        rhs += ","
    if len(observations) > 0:
        rhs += ",".join(observations)
    return "P(" + lhs + " | " + rhs + ")"


def do_calculus(graph: Graph):
    """
    Enter a main REPL area allowing the manipulation of do_calculus
    """

    def process_set(string: str) -> set:
        return set([item.strip() for item in string.split(",")] if string.strip() != "" else [])

    def ensure_no_duplicates(new_set, *compare):
        for other_set in compare:
            if len(new_set & other_set) > 0:
                return False
        return True

    do_calculus_rules = "Rule 1: P(y | do(x), z, w) = P(y | do(x), w) if (Y _||_ Z | X, W) in G(-X)\n" \
                        "Rule 2: P(y | do(x), do(z), w) = P(y | do(x), z, w) if (Y _||_ Z | X, W) in G(-X, Z_)\n" \
                        "Rule 3: P(y | do(x), do(z), w) = P(y | do(x), w) if (Y _||_ Z | X, W) in G(-X, -Z(W))"

    do_calculus_prompt = "To test the 3 rules of do_calculus, we manipulate 4 sets of variables: X, Y, Z, and W.\n" \
                         "In these rules, X and Z may be interventions. The rules are:\n\n" + \
                         do_calculus_rules + \
                         "\n\nPlease enter each, one at a time (when prompted), as a comma-separated list.\n" \
                         "Also, note that any of X, Z, or W may be left empty.\n"

    # We will hold a set of all variables y, x, z, w and manipulate it through user input
    y = None
    x = None
    z = None
    w = None

    while True:

        # No variables yet
        if y is None or x is None or z is None or w is None:

            # We need to validate our input, so just keep trying through Assertions
            while True:
                try:
                    all_sets = []
                    io.write(do_calculus_prompt, console_override=True)

                    y = process_set(input("Please enter set Y, which will not be an intervention: "))
                    all_sets.append(y)

                    x = process_set(input("Please enter all interventions: "))
                    all_sets.append(x)
                    assert ensure_no_duplicates(x, y), "Sets are not disjoint!"

                    w = process_set(input("Please enter all observations: "))
                    all_sets.append(w)
                    assert ensure_no_duplicates(w, x, y), "Sets are not disjoint!"

                except AssertionError:
                    continue

                break

        # Construct all possible sets by splitting interventions / observations
        # The following sets are tentative; not each subset will actually allow the rule to be applied until validated

        # First, all possible Z that can be deleted from our observations
        rule_1_tentative_z = set(power_set(w, False)) | set(power_set(graph.v - (y | w | x), False))
        rule_1_valid_z = [set(s) for s in rule_1_tentative_z if rule_1_applicable(graph, y, x, set(s), w)]

        # Second, all possible Z that can switch between being observation/intervention
        rule_2_tentative_z = set(power_set(w, False)) | set(power_set(x, False))
        rule_2_valid_z = [set(s) for s in rule_2_tentative_z if rule_2_applicable(graph, y, x, set(s), w)]

        # Third, all possible Z that are subsets of our interventions that can be deleted
        rule_3_tentative_z = set(power_set(x, False)) | set(power_set(graph.v - set(y | w | x), False))
        rule_3_valid_z = [set(s) for s in rule_3_tentative_z if rule_3_applicable(graph, y, x, set(s), w)]

        # Present all options to the user
        current_query = query_str(y, x, w, z=z)
        io.write("Our query is currently: " + current_query, console_override=True)

        # Present all options to the user (generating our menu as we go) and then get a selection
        options = []

        # Present all Rule 1 applications
        for r1_set in rule_1_valid_z:

            action = "Delete" if r1_set.issubset(w) else "Insert"
            query_message = "Rule 1: " + action + " Z: " + ",".join(r1_set)
            result = apply_rule_1(graph, y, x, r1_set, w)
            result_str = query_str(*result)
            y_result, x_result, w_result = result
            query_message += ", Making: " + current_query + " -> " + result_str
            options.append([ResultWrapper(y_result, x_result, w_result), query_message])

        # Present all Rule 2 applications
        for r2_set in rule_2_valid_z:

            action = "Drop" if r2_set.issubset(x) else "Insert"
            query_message = "Rule 2: " + action + " as Intervention: " + ",".join(r2_set)
            result = apply_rule_2(graph, y, x, r2_set, w)
            result_str = query_str(*result)
            y_result, x_result, w_result = result
            query_message += ", Making: " + current_query + " -> " + result_str
            options.append([ResultWrapper(y_result, x_result, w_result), query_message])

        # Present all Rule 3 applications
        for r3_set in rule_3_valid_z:

            action = "Delete" if r3_set.issubset(x) else "Insert"
            query_message = "Rule 3: " + action + " Z: " + ",".join(r3_set)
            result = apply_rule_3(graph, y, x, r3_set, w)
            result_str = query_str(*result)
            y_result, x_result, w_result = result
            query_message += ", Making: " + current_query + " -> " + result_str
            options.append([ResultWrapper(y_result, x_result, w_result), query_message])

        # Throw an "exit/return" in
        options.append([ResultWrapper(), "Exit / Return"])

        selection = user_index_selection("All Possible Do-Calculus Applications: ", options)

        # Exit option
        if selection == len(options)-1:
            return

        result = options[selection][0]

        y, x, w = result.data
        z = set()
