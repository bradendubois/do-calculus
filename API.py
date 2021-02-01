###########################################################
#                   probability-code API                  #
###########################################################

from src.api.probability_query import api_probability_query

from src.probability.structures.BackdoorController import BackdoorController
from src.probability.structures.VariableStructures import *
from src.probability.structures.CausalGraph import CausalGraph

from src.util.parsers.GraphLoader import parse_graph_file_data

from itertools import product


class Do:

    def __init__(self, model: dict or None, print_details=False, print_result=False, log_details=False):
        if model:
            data = parse_graph_file_data(model)
            self.load_model(data)

        else:
            self.cg = None
            self.g = None
            self.bc = None

    def load_model(self, data: dict):
        """
        Load a model into the API.
        @param data: A dictionary conforming to the required causal model specification to be loaded
            into the API.
        """
        self.cg = CausalGraph(**data)
        self.g = data["graph"]
        self.bc = BackdoorController(self.g.copy())

    ################################################################
    #                         Distributions                        #
    ################################################################

    #def p(self, p_str):
    #    return self.cg.probability_query(*[parse_outcomes_and_interventions(g) for g in p_str])

    def p(self, y: set, x: set):
        """
        Compute a probability query of Y, given X.
        :param y: Head of query; a set of variable-outcome tuples; Ex: {("Y", "y"), ("Weather", "sunny")}
        :param x: Body of query; a set of variable-outcome tuples; Ex: {("Y", "y"), ("Weather", "sunny")}
        :return: The probability of P(Y | X), in the range [0.0, 1.0]
        """
        # TODO - Interventions
        return api_probability_query(self.cg, y, x)

    ################################################################
    #               Pathfinding (Backdoor Controller)              #
    ################################################################

    def all_deconfounding_sets(self, x: set, y: set):
        return self.bc.get_all_z_subsets(x, y)

    def any_backdoor_paths(self, x: set, y: set, z=None):
        return self.bc.any_backdoor_paths(x, y, z or set())

    def run_backdoor_controller(self, y, x, z=None):
        return set().union(*[set(self.bc.backdoor_paths(s, t, z or set()) for s, t in product(y, x))])

    def all_paths(self, s, t):
        return self.bc.all_paths_cumulative(s, t, [], [])

    def backdoor_paths(self, src: set, dst: set):
        ...

