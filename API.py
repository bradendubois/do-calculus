###########################################################
#                   probability-code API                  #
###########################################################

from src.api.backdoor_paths import api_backdoor_paths
from src.api.deconfounding_sets import api_deconfounding_sets
from src.api.joint_distribution_table import api_joint_distribution_table
from src.api.probability_query import api_probability_query

from src.probability.structures.BackdoorController import BackdoorController
from src.probability.structures.CausalGraph import CausalGraph
from src.probability.structures.ConditionalProbabilityTable import ConditionalProbabilityTable
from src.probability.structures.VariableStructures import Variable

from src.util.ModelLoader import parse_graph_file_data
from src.util.OutputLogger import OutputLogger


class Do:

    def __init__(self, model: dict or None, print_detail=False, print_result=False, log=False, log_fd=None):
        """
        Initializer for an instance of the API.
        @param model: An optional dictionary of a loaded causal graph model. Can be None, and loaded later.
        @param print_detail: Boolean; whether the computation steps involved in queries should be printed.
        @param print_result: Boolean; whether the result of a query should be printed.
        @param log: Boolean; whether the computation steps involved in queries should logged to a file. If this
            is true, a file must have been set to log to. This can be done by providing a file descriptor either as
            an argument to log_fd, or can be done later with a call to set_log_fd.
        @param log_fd: An open file descriptor to write to, if log_details is enabled.
        """
        if model:
            self.load_model(model)

        else:
            self._cg = None
            self._g = None
            self._bc = None

        self._print_result = print_result
        self._output = OutputLogger(print_result, print_detail, log, log_fd)

    ################################################################
    #                       API Modifications                      #
    ################################################################

    def load_model(self, data: dict):
        """
        Load a model into the API.
        @param data: A dictionary conforming to the required causal model specification to be loaded
            into the API.
        """
        d = parse_graph_file_data(data)

        self._cg = CausalGraph(output=self._output, **d)
        self._g = d["graph"]
        self._bc = BackdoorController(self._g.copy())

    def set_print_result(self, to_print: bool):
        """
        Set whether or not to print the result of any API query to standard output
        @param to_print: Boolean; True to print results, False to not print results.
        """
        self._output.set_print_result(to_print)
        self._print_result = to_print

    def set_print_detail(self, to_print: bool):
        """
        Set whether or not to print the computation steps of any API query to standard output
        @param to_print: Boolean; True to print results, False to not print steps.
        """
        self._output.set_print_detail(to_print)

    def set_logging(self, to_log: bool):
        """
        Set whether to log computation steps and results.
        @precondition A file descriptor has been given to the API either in the initializer, or in a call to set_log_fd.
        @param to_log: Boolean; whether or not to log computation steps.
        """
        self._output.set_log(to_log)

    def set_log_fd(self, log_fd):
        """
        Set the internal file descriptor to log computation steps to, if this option is enabled.
        @param log_fd: An open file descriptor to write computation details to.
        """
        self._output.set_log_fd(log_fd)

    ################################################################
    #                         Distributions                        #
    ################################################################

    def p(self, y: set, x: set) -> float:
        """
        Compute a probability query of Y, given X.
        @param y: Head of query; a set of Outcome objects
        @param x: Body of query; a set of Outcome and/or Variable objects
        @return: The probability of P(Y | X), in the range [0.0, 1.0]
        @raise ProbabilityException when the given probability cannot be computed, such as an invalid Outcome
        """
        # All deconfounding is handled by the CG
        result = api_probability_query(self._cg, y, x)
        self._output.result(result)

        return result

    def joint_distribution_table(self) -> list:
        """
        Compute a joint distribution table across the entire model loaded.
        @return: A list of tuples, (Outcomes, P), where Outcomes is a unique set of Outcome objects for the model, and
            P is the corresponding probability.
        """
        result = api_joint_distribution_table(self._cg)

        if self._print_result:
            keys = sorted(self._cg.variables.keys())
            rows = [[",".join(map(str, outcomes)), [], p] for outcomes, p in result]
            rows.append(["Total:", [], sum(map(lambda r: r[1], result))])
            cpt = ConditionalProbabilityTable(Variable(",".join(keys), [], []), [], rows)

            self._output.result(f"Joint Distribution Table for: {','.join(keys)}")
            self._output.result(f"{cpt}")

        return result

    ################################################################
    #               Pathfinding (Backdoor Controller)              #
    ################################################################

    def backdoor_paths(self, src: set, dst: set, dcf: set) -> list:
        """
        Find all the "backdoor paths" between two sets of variables.
        @param src: A set of (string) vertices defined in the loaded model, which will be the source to begin searching
            for paths from, to any vertex in dst
        @param dst: A set of (string) vertices defined in the loaded model, which are the destination vertices to be
            reached by any vertex in src
        @param dcf: A set of (string) vertices which will be considered part of the given deconfounding set as a means
            of blocking (or potentially unblocking) backdoor paths
        @return: A list of lists, where each sub-list is a backdoor path from some vertex in src to some vertex in dst,
            and each vertex within the sub-list is a vertex along this path.
        """
        result = api_backdoor_paths(self._bc, src, dst, dcf)

        if self._print_result:
            for path in result:
                for left, right in zip(path[:-1], path[1:]):
                    print(left, "<-" if right in self._g.parents(left) else "->", end=" ")
                print(path[-1])
        return result

    def deconfounding_sets(self, src: set, dst: set) -> list:
        """
        Find the sets of vertices in the loaded model that are sufficient at blocking all backdoor paths from all
        vertices in src to any vertices in dst
        @param src: A set of (string) vertices defined in the loaded model, acting as the source for backdoor paths
            to find, and have blocked by a sufficient deconfounding set of vertices.
        @param dst: A set of (string) vertices defined in the loaded model, acting as the destination set of vertices
        @return: A list of sets, where each set contains (string) vertices sufficient at blocking all backdoor paths
            between any pair of vertices in src X dst
        """
        result = api_deconfounding_sets(self._bc, src, dst)
        if self._print_result:
            for s in result:
                print("-", ", ".join(map(str, s)))
        return result

    ################################################################
    #                         Graph-Related                        #
    ################################################################

    ################################################################
    #                          Bookkeeping                         #
    ################################################################

    # TODO - Decorator to require the API to have a model loaded
    def require_model(self, function):
        ...
