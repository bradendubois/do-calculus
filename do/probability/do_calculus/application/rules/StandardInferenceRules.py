#########################################################
#                                                       #
#   Standard Inference Rules                            #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Isolate our standard rules of conditioning / distribution

# Pearl outlines 3 rules of do-calculus, yet the actual derivation of a query involving "do" to a query no longer
#   involving "do" usually must condition on certain variables, and so we do need this rule, even though it's not
#   one of the big 3 rules.

from src.probability.structures.Graph import Graph
from src.probability.do_calculus.application.CustomSetFunctions import rename, union
from src.probability.do_calculus.application.QueryStructures import Query, QueryBody, Sigma


###################################################
#      Jeffrey's Rule / Conditioning over Z       #
###################################################


def condition(graph: Graph, y: set, x: set, z: set, w: set):

    # Condition over Z - Don't need to validate / check anything as in do-calculus
    return Sigma(rename(z)), Query(y, QueryBody(x, union(rename(z), w))), Query(rename(z), QueryBody(x, w))


###################################################
#                   Product Rule                  #
###################################################


def apply_product_rule(graph: Graph, y: set, x: set, z: set, w: set):

    # Take this Z set out Y (Z is not actually in the body, but rather Z is simply the "moving" set of variables)
    return Query(y - z, QueryBody(x, w | z)), Query(z, QueryBody(x, w))
