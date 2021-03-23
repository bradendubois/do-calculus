###########################################################
#                   probability-code API                  #
###########################################################

from itertools import product
from pathlib import Path
from typing import Collection, Optional, Sequence, Union

from .api.backdoor_paths import api_backdoor_paths
from .api.deconfounding_sets import api_deconfounding_sets
from .api.joint_distribution_table import api_joint_distribution_table
from .api.probability_query import api_probability_query

from .structures.BackdoorController import BackdoorController
from .structures.CausalGraph import CausalGraph
from .structures.ConditionalProbabilityTable import ConditionalProbabilityTable
from .structures.Graph import Graph
from .structures.Types import Vertex, ProbabilityException
from .structures.VariableStructures import Outcome, Intervention

from .util.ModelLoader import parse_model
from .util.OutputLogger import OutputLogger


class Do:

    def __init__(self, model: Union[str, dict, Path], print_detail=False, print_result=False, log=False, log_fd=None):
        """
        Initializer for an instance of the API.
        @param model: An optional causal model. Can be a string path to a file, a pathlib.Path to a file, a dictionary
        of a valid model. Can also be specified as None, and loaded later using load_model.
        @param print_detail: Boolean; whether the computation steps involved in queries should be printed.
        @param print_result: Boolean; whether the result of a query should be printed.
        @param log: Boolean; whether the computation steps involved in queries should logged to a file. If this
            is true, a file must have been set to log to. This can be done by providing a file descriptor either as
            an argument to log_fd, or can be done later with a call to set_log_fd.
        @raise FileNotFoundError or KeyError if a model is provided but encounters errors in loading. See load_model for
        details on when these exceptions occur.
        """
        self._print_result = print_result
        self._output = OutputLogger(print_result, print_detail, log, log_fd)

        if model:
            self.load_model(model)

        else:
            self._cg = None
            self._g = None
            self._bc = None

    ################################################################
    #                       API Modifications                      #
    ################################################################

    def load_model(self, data: Union[str, dict, Path]):
        """
        Parse and load a model into the API.
        @param data: Any of a string path or pathlib.Path to a file, or a dictionary conforming to the required causal
        model specification.
        @raise FileNotFoundError if a string path or pathlib.Path object does not point to a file, or does not point to
        a file that can be loaded. This can occur if the file does not end in .json, .yml, or .yaml.
        @raise KeyError on issues relating to parsing the model. This can occur if the model does not conform to the
        required specification and is missing an attribute.
        """
        try:
            d = parse_model(data)

            self._cg: CausalGraph = CausalGraph(output=self._output, **d)
            self._g: Graph = d["graph"]
            self._bc: BackdoorController = BackdoorController(self._g.copy())

        except Union[FileNotFoundError, KeyError] as e:
            self._output.detail(str(e))
            raise e

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

    def p(self, y: Collection[Outcome], x: Collection[Union[Outcome, Intervention]]) -> float:
        """
        Compute a probability query of Y, given X. All deconfounding and standard inference rules are handled by the
        Causal Graph automatically.
        @param y: The head of a query; a collection of Outcome objects.
        @param x: The body of a query; a collection of Outcome and/or Intervention objects
        @return: The probability, P(Y | X), as a float in the range [0.0, 1.0]
        @raise AssertionError If two results differ by a significant margin; this indicates a fault with the software,
        not with the model or query.
        @raise InvalidOutcome If a given Outcome or Intervention does not exist in the model, or the specified value
        is not a valid outcome of the respective Variable.
        @raise NoDeconfoundingSet If there does not exist a sufficient set of deconfounding variables in the model to
        block all backdoor paths from x->y.
        @raise ProbabilityIndeterminableException if the query can not be completed for any reason. With a consistent
        model, this should never occur.
        """
        try:
            result = api_probability_query(self._cg, y, x)
            self._output.result(result)
            return result

        except Union[AssertionError, ProbabilityException] as e:
            self._output.detail(e)
            raise e

    def joint_distribution_table(self) -> ConditionalProbabilityTable:
        """
        Compute a singular ConditionalProbabilityTable across the joint distribution of the model.
        @return: A ConditionalProbabilityTable representing the each possible joint outcome of the model.
        """

        result: ConditionalProbabilityTable = api_joint_distribution_table(self._cg)

        if self._print_result:
            self._output.result(f"Joint Distribution Table for: {','.join(sorted(self._cg.variables.keys()))}")
            self._output.result(f"{result}")

        return result

    ################################################################
    #               Pathfinding (Backdoor Controller)              #
    ################################################################

    def backdoor_paths(self, src: Collection[Vertex], dst: Collection[Vertex], dcf: Optional[Collection[Vertex]]) -> Collection[Sequence[str]]:
        """
        Find all backdoor paths between two collections of variables in the model.
        @param src: A collection of variables defined in the model, which will be the source to begin searching for
            paths from, to any vertex in dst
        @param dst: A collection of variables defined in the model, which are the destination vertices to be reached by
            any vertex in src
        @param dcf: An optional set of variables defined in the model, which will be considered part of the given
            deconfounding set as a means of blocking (or potentially unblocking) backdoor paths. To indicate no
            deconfounding variables, an empty collection or None can be specified.
        @return: A collection of paths, where each path is represented as a sequence of (string) vertices. Each path
            is ordered (endpoints in src and dst included) preserving the order of the path.
        @raise: IntersectingSets if any of src, dst, and dcf have any intersection.
        """
        result = api_backdoor_paths(self._bc, src, dst, dcf)

        if self._print_result:
            for path in result:
                for left, right in zip(path[:-1], path[1:]):
                    print(left, "<-" if right in self._g.parents(left) else "->", end=" ")
                print(path[-1])

        return result

    def standard_paths(self, src: Collection[Vertex], dst: Collection[Vertex]) -> Collection[Sequence[str]]:
        """
        Find all "standard" paths from any pair vertices in the product of some source and destination set of vertices.
        @param src: A collection of vertices from which to search for a path to dst.
        @param dst: A collection of vertices that will be reached from src.
        @return: A collection of paths, where each path is represented as a sequence of string vertices in the graph,
        (endpoints in src and dst included), the order of which represents the path.
        @raise: IntersectingSets if src and dst have any intersection.
        """
        paths = set()
        for s, t in product(src, dst):
            paths.update(self._bc.all_paths_cumulative(s, t))
        self._output.result(paths)
        return paths

    def deconfounding_sets(self, src: Collection[Vertex], dst: Collection[Vertex]) -> Collection[Collection[str]]:
        """
        Find the sets of vertices in the model that are sufficient at blocking all backdoor paths from all vertices in
        src to any vertices in dst
        @param src: A collection of vertices defined in the model, acting as the source for backdoor paths to find,
            and have blocked by a sufficient deconfounding set of vertices.
        @param dst: A collection of vertices defined in the model, acting as the destination set of vertices
        @return: A collection of sufficient deconfounding sets, where each deconfounding set consists of a collection of
         (string) vertices sufficient at blocking all backdoor paths between any pair of vertices in (src X dst).
        @raise: IntersectingSets if src and dst have any intersection.
        """

        result = api_deconfounding_sets(self._bc, src, dst)

        if self._print_result:
            for s in result:
                print("-", ", ".join(map(str, s)))

        return result

    def independent(self, s: Collection[Vertex], t: Collection[Vertex], dcf: Optional[Collection[Vertex]]) -> bool:
        """
        Determine if two sets of vertices in the model are conditionally independent, given an optional third set of
        deconfounding vertices.
        @param s: A collection of vertices in the model.
        @param t: A collection of destination vertices in the model.
        @param dcf: An optional collection of deconfounding vertices in the model to block backdoor paths between s and
        t. This can also be an empty set, or explicitly set to None.
        @return: True if all vertices in s and t are conditionally independent.
        @raise: IntersectingSets if any of s, t, and dcf have any intersection.
        """
        independent = all(self._bc.independent(s, t, dcf) for (s, t) in product(s, t))
        self._output.result(f"{s} x {t}: {independent}")
        return independent

    ################################################################
    #                         Graph-Related                        #
    ################################################################

    def roots(self) -> Collection[Vertex]:
        """
        Find all roots in the graph, where a root is defined as any vertex with no ancestors. This definition contrasts
        with some causal inference literature, in which a root is actually defined as any vertex with no descendants.
        @return: A collection of all vertices in the graph with no ancestors.
        """
        roots = self._g.roots()
        self._output.result(roots)
        return roots

    def sinks(self) -> Collection[Vertex]:
        """
        Find all sinks in the graph, where a sink is defined as any vertex with no descendants.
        @return: A collection of all vertices in the graph with no descendants.
        """
        sinks = self._g.sinks()
        self._output.result(sinks)
        return sinks

    def parents(self, v: Vertex) -> Collection[Vertex]:
        """
        Find all parents in the graph of some given vertex. A parent is defined as a vertex p such that (p, v) exists
        in E, the collection of edges comprising the graph.
        @param v: Some vertex defined in the graph.
        @return: A collection of all parents of v.
        """
        parents = self._g.parents(v)
        self._output.result(parents)
        return parents

    def children(self, v: Vertex) -> Collection[Vertex]:
        """
        Find all children in the graph of some given vertex. A child is defined as a vertex c such that (v, c) exists
        in E, the collection of edges comprising the graph.
        @param v: Some vertex defined in the graph.
        @return: A collection of all children of v.
        """
        children = self._g.children(v)
        self._output.result(children)
        return children

    def ancestors(self, v: Vertex) -> Collection[Vertex]:
        """
        Find all ancestors in the graph of some given vertex. An ancestors is defined as a vertex a such that a directed
        path (p, x1, ... xi, v) in E, the collection of edges comprising the graph.
        @param v: Some vertex defined in the graph.
        @return: A collection of all ancestors of v.
        """
        ancestors = self._g.ancestors(v)
        self._output.result(ancestors)
        return ancestors

    def descendants(self, v: Vertex) -> Collection[Vertex]:
        """
        Find all descendants in the graph of some given vertex. A descendant is defined as a vertex d such that a
        directed path (v, x1, ... xi, d) in E, the collection of edges comprising the graph.
        @param v: Some vertex defined in the graph.
        @return: A collection of all descendants of v.
        """
        descendants =  self._g.descendants(v)
        self._output.result(descendants)
        return descendants

    def topology(self) -> Sequence[Vertex]:
        """
        Get a topological ordering of all vertices defined in the graph. A topological ordering is some sequence of the
        N vertices in the graph, V1, ..., VN such that for any i, j | 1 <= i < j <= N, Vj is not an ancestor of Vi.
        @return: A sequence of vertices defining a topological ordering, V1, ..., VN.
        """
        topology = self._g.topology_sort()
        self._output.result(topology)
        return topology

    def topology_position(self, v: Vertex) -> int:
        """
        Find the position of some given vertex in a topological ordering of the graph.
        @param v: Some vertex defined in the graph.
        @return: An integer i in the range [1, N] representing the index of vertex v such that Vi = v in the
        topological ordering of G, given as 1 <= Vi <= Vn.
        """
        topology = self._g.get_topology(v)
        self._output.result(topology)
        return topology
