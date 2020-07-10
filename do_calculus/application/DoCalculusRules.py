#########################################################
#                                                       #
#   Do-Calculus Rules                                   #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# The actual rules of do-calculus; so short, so succinct!

from probability_structures.Graph import Graph
from probability_structures.BackdoorController import BackdoorController


#################################################
#   Rule 1 - Insertion/deletion of observation  #
#################################################


def rule_1_applicable(graph: Graph, y: set, x: set, z: set, w: set) -> bool:

    # Disable the incoming X edges
    graph.reset_disabled()
    graph.disable_incoming(*x)

    # See if Y _||_ Z
    independent = BackdoorController(graph).independent(y, z, x | (w-z))
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
    graph.disable_incoming(*x-z)
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
    graph.disable_incoming(*x-z)
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
