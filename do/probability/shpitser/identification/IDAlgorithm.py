#########################################################
#                                                       #
#   IDAlgorithm                                         #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

from src.probability.shpitser.structures.Expressions import SigmaObj, PiObj
from src.probability.shpitser.structures.Distribution import Distribution
from src.probability.shpitser.structures.LatentGraph import LatentGraph

# This is the implementation of Shpitser & Pearl (2006)'s 3rd algorithm, which provides an identification of
#   an interventional distribution using observational distributions, without any of Pearl's backdoor criterion.

# Some preliminaries to simplify the notation used in the algorithm


# Custom exception to match the ID algorithm failure
class FAIL(Exception):
    def __init__(self, g, cg):
        self.g = g
        self.cg = cg


# noinspection PyPep8Naming
def C(G: LatentGraph):
    return G.all_c_components()


# noinspection PyPep8Naming
def Sigma(s, X):
    return SigmaObj(s, X)


# noinspection PyPep8Naming
def Pi(s, X):
    return PiObj(s, X)


# noinspection PyPep8Naming
def ID(y: set, x: set, P: Distribution, G: LatentGraph, rec=0):

    # noinspection PyPep8Naming
    def An(X: set):
        return set().union(*[G.ancestors(v) for v in X]) | X

    def parents(v):
        print(v, G.parents(v))
        return G.parents(v)

    V = G.v

    # ID

    # 1 - if X == {}
    if x == set():

        # return Sigma_{v\y}P(v)
        return Sigma(set(), [P(y)])

    # 2 - if V != An(Y)_G
    if V != An(y):

        # return ID(y, x ∩ An(Y)_G, P(An(Y)), An(Y)_G)
        return ID(y, x & An(y), P(An(y)), G(An(y)), rec+1)

    # 3 - let W = (V\X) \ An(Y)_{G_X}.
    G.disable_incoming(*x)
    W = (V - x) - An(y)
    G.reset_disabled()

    # if W != {}
    if W != set():

        # return ID(y, x ∪ w, P, G)
        return ID(y, x | W, P, G, rec+1)

    # 4 - if C(G\X) == { S_1, ..., S_k},
    if len(S := C(G(V - x))) > 1:

        # return Sigma_{v\(y ∪ x)} Pi_i id_algorithm(s_i, v \ s_i, P, G)
        return Sigma(V - (y | x), Pi(S, [ID(s, V - s, P, G, rec+1) for s in S]))

    #   if C(G \ X) == {S},
    if len(C(G(V - x))) == 1:

        S = S[0]  # Simplify; S is currently a list of one component, so make S the component itself

        #   5 - if C(G) == {G}
        if C(G) == G:
            # throw FAIL(G, S)
            raise FAIL(G, C(G))

        #   6 - if S ∈ C(G)
        if S in C(G):

            # return Sigma_{S\Y} Pi_{V_i ∈ S} P(v_i | v_P{pi}^{i -1})
            return Sigma(S-y, Pi(S, [P(Vi, parents(Vi)) for Vi in S]))

        #   7 -  if (∃S')S ⊂ S' ∈ C(G)
        if any(S.issubset(Si) for Si in C(G)):

            Si = [Si for Si in C(G) if S.issubset(Si)][0]

            # return ID(y, x ∩ S', Pi_{V_i ∈ S'} P(V_i | V_{pi}^{i-1} ∩ S', v_{pi}^{i-1} \ S'), S')
            return ID(y, x & Si, P, G(Si))

    raise FAIL(G, C(G))
