#########################################################
#                                                       #
#   Backdoor Controller                                 #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

from itertools import product
from typing import List, Optional

from .Graph import Graph
from .Types import Collection, Path, Vertices, Vertex, V_Type

from ..config.settings import Settings
from ..util.helpers import minimal_sets, power_set, str_map


class BackdoorController:
    """
    A specific class used to break up the main Causal Graph; Backdoor paths are found here, as defined by Judea Pearl
    in Causality / Book of Why / etc.
    """

    def __init__(self, graph: Graph):
        """
        Initialize a BackdoorController, capable of finding backdoor paths, and sufficient "blocking" sets of
        deconfounder variables.
        @param graph: A Graph class used to identify paths in.
        """
        self.graph = graph.copy()
        self.graph.reset_disabled()

    def backdoor_paths(self, src: Vertices, dst: Vertices, dcf: Optional[Vertices]) -> List[Path]:
        """
        Get all possible backdoor paths between some source set of vertices in the internal graph to any vertices in
        some destination set of vertices. A given (possibly empty) set of deconfounding vertices may serve to block, or
        even open, some backdoor paths.
        @param src: The source set of (string) vertices to search for paths from
        @param dst: The destination set of (string) vertices to search from src towards.
        @param dcf: An optional set of (string) vertices that may serve as a sufficient deconfounding set to block or open
            backdoor paths.
        @return: A list of lists, where each sublist contains a backdoor path, the first and last element being a
            vertex from src and dst, respectively, with all vertices between representing the path. All elements are
            string vertices.
        """

        paths = []

        src_str = str_map(src)
        dst_str = str_map(dst)
        dcf_str = str_map(dcf) if dcf else set()

        # Use the product of src, dst to try each possible pairing
        for s, t in product(src_str, dst_str):
            paths += self._backdoor_paths_pair(s, t, dcf_str)

        return paths

    def _backdoor_paths_pair(self, s: Collection[str], t: Collection[str], dcf: Collection[str]) -> List[Path]:
        """
        Find all backdoor paths between any particular pair of vertices in the loaded graph
        @param s: A source (string) vertex in the graph
        @param t: A destination (string) vertex in the graph
        @param dcf: A set of (string) variables, by which movement through any variable is controlled. This can serve
            as a sufficient "blocking" set, or may open additional backdoor paths
        @return Return a list of lists, where each sublist is a path of string vertices connecting s and t.
            Endpoints s and t are the first and last elements of any sublist.
        """

        def get_backdoor_paths(cur: str, path: list, path_list: list, previous="up") -> list:
            """
            Return a list of lists of all paths from a source to a target, with conditional movement of either
                child to parent or parent to child. This may include an edge case that is not a backdoor path, which
                is filtered in the parent function, otherwise all paths will be backdoor paths.
            This is a heavily modified version of the graph-traversal algorithm provided by Dr. Eric Neufeld.
            @param cur: The current (string) vertex we are at in a traversal.
            @param path: The current path from s, our source.
            @param path_list: A list of lists, each sublist being a path discovered so far.
            @param previous: Whether moving from the previous variable to current we moved "up" (child to parent) or
                "down" (from parent to child); this movement restriction is involved in backdoor path detection
            @return: A list of lists, where each sublist is a path from s to t.
            """

            # Reached target
            if cur == t:
                return path_list + [path + [t]]

            # No infinite loops
            if cur not in path:

                if previous == "down":

                    # We can ascend on a controlled collider, OR an ancestor of a controlled collider
                    if cur in dcf or any(map(lambda v: v in dcf, self.graph.reach(cur))):
                        for parent in self.graph.parents(cur):
                            path_list = get_backdoor_paths(parent, path + [cur], path_list, "up")

                    # We can *continue* to descend on a non-controlled variable
                    if cur not in dcf:
                        for child in self.graph.children(cur):
                            path_list = get_backdoor_paths(child, path + [cur], path_list, "down")

                if previous == "up" and cur not in dcf:

                    # We can ascend on a non-controlled variable
                    for parent in self.graph.parents(cur):
                        path_list = get_backdoor_paths(parent, path + [cur], path_list, "up")

                    # We can descend on a non-controlled reverse-collider
                    for child in self.graph.children(cur):
                        path_list = get_backdoor_paths(child, path + [cur], path_list, "down")

            return path_list

        # Get all possible backdoor paths
        backdoor_paths = get_backdoor_paths(s, [], [])

        # Filter out the paths that don't "enter" x; see the definition of a backdoor path
        return list(filter(lambda l: l[0] in self.graph.children(l[1]) and l[1] != t, backdoor_paths))

    def all_dcf_sets(self, src: Vertices, dst: Vertices) -> List[Collection[str]]:
        """
        Finds all Z subsets that serve as deconfounding sets between two sets of vertices, such as for the purpose of
        measuring interventional distributions.
        @param src: Some set of (string) vertices in the graph
        @param dst: Some set of (string) vertices, which we want to find sets Z to give independence from X
        @return: A list of sets, each set representing a set of variables that are a sufficient Z set
        """

        src_str = str_map(src)
        dst_str = str_map(dst)

        # Can't use anything in src, dst, or any descendant of any vertex in src as a deconfounding/blocking vertex
        disallowed_vertices = src_str | dst_str | set().union(*[self.graph.reach(s) for s in src_str])

        valid_deconfounding_sets = list()

        # Candidates deconfounding sets remaining are the power set of all the possible remaining vertices
        for tentative_dcf in power_set(self.graph.v - disallowed_vertices):

            # Tentative, indicating that no specific cross product in this subset has yet yielded any backdoor paths
            any_backdoor_paths = False

            # Cross represents one (x in X, y in Y) tuple
            for s, t in product(src_str, dst_str):

                # Get any/all backdoor paths for this particular pair of vertices in src,dst with given potential
                #   deconfounding set
                backdoor_paths = self._backdoor_paths_pair(s, t, set(tentative_dcf))

                if len(backdoor_paths) > 0:
                    any_backdoor_paths = True
                    break

            # None found in any cross product -> Valid subset
            if not any_backdoor_paths:
                valid_deconfounding_sets.append(tentative_dcf)

        # Minimize the sets, if enabled
        if Settings.minimize_backdoor_sets:
            valid_deconfounding_sets = minimal_sets(*valid_deconfounding_sets)

        return list(valid_deconfounding_sets)

    def all_paths_cumulative(self, s: str, t: str, path: list, path_list: list) -> List[Path]:
        """
        Return a list of lists of all paths from a source to a target, with conditional movement from child to parent,
        or parent to child.
        This is a modified version of the graph-traversal algorithm provided by Dr. Eric Neufeld.
        @param s: A source (string) vertex defined in the graph.
        @param t: A target (string) destination vertex defined in the graph.
        @param path: A list representing the current path at any given point in the traversal.
        @param path_list: A list which will contain lists of paths from s to t.
        @return: A list of lists of Variables, where each sublist denotes a path from s to t .
        """
        if s == t:
            return path_list + [path + [t]]
        if s not in path:
            for child in self.graph.children(s):
                path_list = self.all_paths_cumulative(child, t, path + [s], path_list)
        return path_list

    def independent(self, src: Vertices, dst: Vertices, dcf: Optional[Vertices]) -> bool:
        """
        Helper function that makes some do_calculus logic more readable; determine if two sets are independent, given
        some third set.
        @param src: A source set (of strings) X, to be independent from Y
        @param dst: A destination set (of strings) Y, to be independent from X
        @param dcf: A deconfounding set (of strings) Z, to block paths between X and Y
        @return: True if there are no backdoor paths and no straight-line paths, False otherwise
        """

        src_str = str_map(src)
        dst_str = str_map(dst)
        dcf_str = str_map(dcf) if dcf else set()

        # Not independent if there are any unblocked backdoor paths
        if len(self.backdoor_paths(src_str, dst_str, dcf_str)) > 0:
            return False

        # Ensure no straight-line variables from any X -> Y or Y -> X
        for s, t in product(src_str, dst_str):
            if len(self.all_paths_cumulative(s, t, [], [])) != 0:
                return False        # x -> y
            if len(self.all_paths_cumulative(t, s, [], [])) != 0:
                return False        # y -> x

        # No paths, must be independent
        return True
