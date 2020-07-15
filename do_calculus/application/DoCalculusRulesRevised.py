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
from do_calculus.QueryList import *

#################################################
#   Rule 1 - Insertion/deletion of observation  #
#################################################


def rule_1_applicable(graph: Graph, y: set, x: set, z: set, w: set) -> bool:

    # Disable the incoming X edges
    graph.reset_disabled()
    graph.disable_incoming(*x)

    # See if Y _||_ Z
    independent = BackdoorController(graph).independent(y, z, x | (w-z))
    graph.reset_disabled()
    # print(str(y), str(x), str(z), str(w), independent)

    return independent


def apply_rule_1(graph: Graph, y: set, x: set, z: set, w: set):

    # Double check
    assert rule_1_applicable(graph, y, x, z, w), "Rule 1 not applicable!"

    # Deleting Z from W if it's already in W
    if z.issubset(w):
        return Query(y, VariableSet(x, w - z))

    # Not in W - inserting Z
    else:
        return Sigma(rename(z)), Query(y, VariableSet(x, w | rename(z))), Query(rename(z), VariableSet(x, w))


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
    graph.reset_disabled()
    # print(str(y), str(x), str(z), str(w), independent)

    return independent


def apply_rule_2(graph: Graph, y: set, x: set, z: set, w: set):

    # Double check
    assert rule_2_applicable(graph, y, x, z, w), "Rule 2 is not applicable!"

    # Dropping z from Interventions X if that is where it currently is
    if z.issubset(x):
        return Query(y, VariableSet(x - z, w | z))

    # Dropping it from our Observations
    else:
        return Query(y, VariableSet(x | z, w - z))


###################################################
#   Rule 3 - Insertion/deletion of actions        #
###################################################

def rule_3_applicable(graph: Graph, y: set, x: set, z: set, w: set):

    # Disable X incoming edges, all edges incoming to any non-ancestor of any W node in G ^X
    graph.reset_disabled()
    graph.disable_incoming(*x-z)
    all_w_ancestors = set().union(*[graph.ancestors(v) for v in w])
    zw = z - all_w_ancestors
    graph.disable_incoming(*zw)

    # See if Y _||_ Z
    independent = BackdoorController(graph).independent(y, z, x | w)
    graph.reset_disabled()
    # print(str(y), str(x), str(z), str(w), independent)

    return independent


def apply_rule_3(graph: Graph, y: set, x: set, z: set, w: set):

    # Double check
    assert rule_3_applicable(graph, y, x, z, w), "Rule 3 is not applicable!"

    # Dropping Z from interventions X
    if z.issubset(x):
        return Query(y, VariableSet(x - z, w))

    # Inserting Z into interventions X, summation
    else:
        return Sigma(z), Query(y, VariableSet(x | z, w)), Query(z, VariableSet(x, w))


###################################################
#   Rule 4 - Jeffrey's Rule Introduction of Z     #
###################################################

def secret_rule_4_applicable(graph: Graph, y: set, x: set, z: set, w: set):

    # Reset graph, see if the introduction of Z blocks paths
    graph.reset_disabled()

    # Ensure that Z acts as a valid deconfounding set
    d_separated = BackdoorController(graph).independent(y, x, z)

    # Z will block paths and is not already in the query
    return d_separated and len(z & w) == 0


def apply_secret_rule_4(graph: Graph, y: set, x: set, z: set, w: set):

    # Double check
    assert secret_rule_4_applicable(graph, y, x, z, w), "Secret Rule 4 is not applicable!"

    # Condition over Z
    return Sigma(z), Query(y, VariableSet(x, z | w)), Query(z, VariableSet(x, w))
