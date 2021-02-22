#########################################################
#                                                       #
#   IDProcessing                                        #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

import itertools

from src.probability.shpitser.structures.Distribution import Distribution
from src.probability.shpitser.structures.Expressions import Symbol, PiObj, SigmaObj

from src.probability.structures.CausalGraph import CausalGraph
from src.probability.structures.VariableStructures import Outcome


# Parse an Expression object produced by the application of Shpitser & Pearl's ID algorithm


def parse_shpitser(result: Symbol, cg: CausalGraph, known: dict):

    if known is None:
        known = dict()

    # Summation
    if isinstance(result, SigmaObj):
        if result.s is None or len(result.s) == 0:
            if isinstance(result.exp, list):
                i = 0.0
                for item in result.exp:
                    i += parse_shpitser(item, cg, known)
                return i
            return parse_shpitser(result.exp, cg, known)
        else:
            outcomes = list(result.s)
            cross = itertools.product(*[cg.outcomes[v] for v in outcomes])
            total = 0
            for c in cross:
                for o in range(len(outcomes)):
                    known[outcomes[o]] = c[o]

                if isinstance(result.exp, list):
                    for item in result.exp:
                        total += parse_shpitser(item, cg, known)
                else:
                    total += parse_shpitser(result.exp, cg, known)

            return total

    # Product
    elif isinstance(result, PiObj):

        if isinstance(result.exp, list):
            prod = 1.0
            for item in result.exp:
                prod *= parse_shpitser(item, cg, known)
            return prod
        else:
            return parse_shpitser(result.exp, cg, known)

    # Compute probability
    elif isinstance(result, Distribution):
        h = result.tables
        b = result.given

        head = []
        for key in h:
            if key not in known:
                value = cg.outcomes[key][0]
            else:
                value = known[key]
            head.append(Outcome(key, value))

        body = []
        if b is not None:
            for key in b:
                if key not in known:
                    value = cg.outcomes[key][0]
                else:
                    value = known[key]
                body.append(Outcome(key, value))

        return cg.probability_query(head, body)

    else:
        print("UNCERTAIN:", type(result))
