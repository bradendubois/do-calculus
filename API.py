###########################################################
#                   probability-code API                  #
###########################################################

from itertools import product


from src.api.probability_query import api_probability_query

from src.probability.structures.BackdoorController import BackdoorController
from src.probability.structures.CausalGraph import CausalGraph

from src.util.parsers.GraphLoader import parse_graph_file_data


class Do:

    def __init__(self, model: dict or None, print_details=False, print_result=False, log_details=False, log_fd=None):
        """
        Initializer for an instance of the API.
        @param model: An optional dictionary of a loaded causal graph model. Can be None, and loaded later.
        @param print_details: Boolean; whether the computation steps involved in queries should be printed.
        @param print_result: Boolean; whether the result of a query should be printed.
        @param log_details: Boolean; whether the computation steps involved in queries should logged to a file. If this
            is true, a file must have been set to log to. This can be done by providing a file descriptor either as
            an argument to log_fd, or can be done later with a call to set_log_fd.
        @param log_fd: An open file descriptor to write to, if log_details is enabled.
        """
        if model:
            data = parse_graph_file_data(model)
            self.load_model(data)

        else:
            self._cg = None
            self._g = None
            self._bc = None
        self._log = log_details
        self._logging_fd = log_fd or None

    ################################################################
    #                       API Modifications                      #
    ################################################################

    def load_model(self, data: dict):
        """
        Load a model into the API.
        @param data: A dictionary conforming to the required causal model specification to be loaded
            into the API.
        """
        self._cg = CausalGraph(**data)
        self._g = data["graph"]
        self._bc = BackdoorController(self._g.copy())

    def set_logging(self, log: bool):
        """
        Set whether to log computation steps.
        @precondition A file descriptor has been given to the API either in the initializer, or in a call to set_log_fd.
        @param log: Boolean; whether or not to log computation steps.
        """
        self._log = log

    def set_log_fd(self, log_fd):
        """
        Set the internal file descriptor to log computation steps to, if this option is enabled.
        @param log_fd: An open file descriptor to write computation details to.
        """
        self._logging_fd = log_fd

    ################################################################
    #                         Distributions                        #
    ################################################################

    def p(self, y: set, x: set):
        """
        Compute a probability query of Y, given X.
        @param y: Head of query; a set of Outcome objects
        @param x: Body of query; a set of Outcome and/or Variable objects
        @return: The probability of P(Y | X), in the range [0.0, 1.0]
        @raise ProbabilityException when the given probability cannot be computed, such as an invalid Outcome
        """
        # All deconfounding is handled by the CG
        return api_probability_query(self._cg, y, x)




    # TODO - Everything below

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
