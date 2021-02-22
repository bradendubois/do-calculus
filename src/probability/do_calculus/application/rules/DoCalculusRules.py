#########################################################
#                                                       #
#   Do-Calculus Rules                                   #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# The actual rules of do-calculus; so short, so succinct!

from src.probability.do_calculus.application.QueryStructures import Query, QueryBody
from src.probability.do_calculus.application.CustomSetFunctions import clean, subtract, union
from src.probability.structures.BackdoorController import BackdoorController
from src.probability.structures.Graph import Graph

#################################################
#   Rule 1 - Insertion/deletion of observation  #
#################################################


def rule_1_applicable(graph: Graph, y: set, x: set, z: set, w: set) -> bool:

    # Disable the incoming X edges
    graph.reset_disabled()
    graph.disable_incoming(*clean(x))

    # See if Y _||_ Z
    independent = BackdoorController(graph).independent(clean(y), clean(z), clean(union(x, subtract(w, z))))
    graph.reset_disabled()
    # print(str(y), str(x), str(z), str(w), independent)

    return independent


def apply_rule_1(graph: Graph, y: set, x: set, z: set, w: set):

    # Double check
    assert rule_1_applicable(graph, y, x, z, w), "Rule 1 not applicable!"

    # Deleting Z from W if it's already in W
    if clean(z).issubset(clean(w)):
        return Query(y, QueryBody(x, subtract(w, z)))

    # Not in W - inserting Z
    else:
        return Query(y, QueryBody(x, union(w, z)))
        # return Sigma(rename(z)), Query(y, QueryBody(x, union(w, rename(z)))), Query(rename(z), QueryBody(x, w))


###################################################
#   Rule 2 - Action/observation exchange          #
###################################################

def rule_2_applicable(graph: Graph, y: set, x: set, z: set, w: set):

    # Disable incoming X edges, outgoing Z edges
    graph.reset_disabled()
    graph.disable_incoming(*clean(subtract(x, z)))
    graph.disable_outgoing(*clean(z))

    # See if Y _||_ Z
    independent = BackdoorController(graph).independent(clean(y), clean(z), clean(union(x, w)))
    graph.reset_disabled()
    # print(str(y), str(x), str(z), str(w), independent)

    return independent


def apply_rule_2(graph: Graph, y: set, x: set, z: set, w: set):

    # Double check
    assert rule_2_applicable(graph, y, x, z, w), "Rule 2 is not applicable!"

    # Dropping z from Interventions X if that is where it currently is
    if clean(z).issubset(clean(x)):
        return Query(y, QueryBody(subtract(x, z), union(w, z)))

    # Dropping it from our Observations
    else:
        # print(x, z, union(x, z))
        return Query(y, QueryBody(union(x, z), subtract(w, z)))


###################################################
#   Rule 3 - Insertion/deletion of actions        #
###################################################

def rule_3_applicable(graph: Graph, y: set, x: set, z: set, w: set):

    # Disable X incoming edges, all edges incoming to any non-ancestor of any W node in G ^X
    graph.reset_disabled()
    graph.disable_incoming(*subtract(x, z))
    all_w_ancestors = set().union(*[graph.ancestors(clean(v)) for v in w])
    zw = subtract(z, all_w_ancestors)
    graph.disable_incoming(*zw)

    # See if Y _||_ Z
    independent = BackdoorController(graph).independent(clean(y), clean(z), union(x, w))
    graph.reset_disabled()
    # print(str(y), str(x), str(z), str(w), independent)

    return independent


def apply_rule_3(graph: Graph, y: set, x: set, z: set, w: set):

    # Double check
    assert rule_3_applicable(graph, y, x, z, w), "Rule 3 is not applicable!"

    # Dropping Z from interventions X
    if clean(z).issubset(clean(x)):
        return Query(y, QueryBody(subtract(x, z), w))

    # Inserting Z into interventions X, summation
    else:
        return Query(y, QueryBody(union(x, z), w))
        # return Sigma(z), Query(y, QueryBody(union(x, z), w)), Query(z, QueryBody(x, w))
