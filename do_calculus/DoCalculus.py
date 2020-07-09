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


class VariableSet:

    def __init__(self, y: set, do_x: set, modify_z: set, observe_w: set, z_is_intervention: bool):

        # Save each of the sets
        self.y = y
        self.do_x = do_x
        self.modify_z = modify_z
        self.observe_w = observe_w

        # In all Pearl's examples, Z is the set that is deleted / changed between see(Z) and do(Z)
        self.z_is_intervention = z_is_intervention


# Rule 1

def rule_1_applicable(graph: Graph, variables: VariableSet) -> bool:

    if variables.modify_z:
        return False

    # G(-X)

    # First, lets disable the incoming X edges
    graph.disable_incoming(variables.do_x)

    # Need a backdoor controller to see if Y and Z are independent
    bc = BackdoorController(graph)

    return bc.independent(variables.y, variables.modify_z, variables.do_x | variables.observe_w)


# TODO - Restructure so there's only one "rule 1 application" function

def rule_1_remove_z(graph: Graph, variables: VariableSet) -> VariableSet:

    assert rule_1_applicable(graph.copy(), variables), "Can't actually remove Z! Rule 1 does not apply"
    assert not variables.z_is_intervention, "Can't remove Z by Rule 1 if it's an intervention"
    return VariableSet(variables.y, variables.do_x, set(), variables.observe_w, False)


def rule_1_add_z(graph: Graph, variables: VariableSet, z: set) -> VariableSet:

    assert len(variables.modify_z) == 0, "Z is not empty, can't add to it by Rule 1!"
    variable_set = VariableSet(variables.y, variables.do_x, z, variables.observe_w, False)
    assert BackdoorController(graph).independent(variables.y, variables.modify_z, variables.do_x | variables.observe_w), "Variables are not independent, Rule 1 should not have been applied!"
    return variable_set


# Rule 2

def rule_2_applicable(graph: Graph, variables: VariableSet):

    graph.disable_incoming(variables.do_x)
    graph.disable_outgoing(variables.modify_z)

    # Need a backdoor controller to see if Y and Z are independent
    bc = BackdoorController(graph)

    return bc.independent(variables.y, variables.modify_z, variables.do_x | variables.observe_w)


def apply_rule_2(graph: Graph, variables: VariableSet):

    assert rule_2_applicable(graph, variables), "Rule 2 is not applicable!"

    return VariableSet(variables.y, variables.do_x, variables.modify_z, variables.observe_w, not variables.z_is_intervention)


# Rule 3

def rule_3_applicable(graph: Graph, variables: VariableSet):

    if not variables.z_is_intervention:
        return False

    graph.disable_incoming(variables.do_x)
    all_w_ancestors = set().union(*[graph.full_ancestors(v) for v in variables.observe_w])
    zw = variables.modify_z - all_w_ancestors
    graph.disable_incoming(zw)

    # Need a backdoor controller to see if Y and Z are independent
    bc = BackdoorController(graph)

    return bc.independent(variables.y, variables.modify_z, variables.do_x | variables.observe_w)


def apply_rule_3_delete_z(graph: Graph, variables: VariableSet):

    assert rule_3_applicable(graph, variables), "Rule 3 is not applicable!"

    return VariableSet(variables.y, variables.do_x, variables.modify_z, variables.observe_w, not variables.z_is_intervention)


def do_calculus():
    """
    Enter a main REPL area allowing the manipulation of do_calculus
    """

    do_calculus_prompt = "To test the 3 rules of do_calculus, we will need 4 sets of variables: X, Y, Z, and " \
                         "W.\nIn these rules, X and Z may be interventions. The rules are:\n" \
                         "Rule 1: P(y | do(x), z, w) = P(y | do(x), w) if (Y _||_ Z | X, W) in G(-X)\n" \
                         "Rule 2: P(y | do(x), do(z), w) = P(y | do(x), z, w) if (Y _||_ Z | X, W) in G(-X, Z_)\n" \
                         "Rule 3: P(y | do(x), do(z), w) = P(y | do(x), w) if (Y _||_ Z | X, W) in G(-X, -Z(W))"

