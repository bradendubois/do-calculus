#########################################################
#                                                       #
#   Backdoor Controller                                 #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

import itertools

from python.probability_structures.Graph import Graph
from python.probability_structures.VariableStructures import Variable
from python.util.IO_Logger import *
from python.util.helpers.MinimizeSets import minimal_sets
from python.util.helpers.PowerSet import power_set


class BackdoorController:
    """
    A specific class used to break up the main Causal Graph; Backdoor paths are found here, as defined by Judea Pearl
    in Causality / Book of Why / etc.
    """

    get_x_set_prompt = \
        "\nEnter a comma-separated list of variables, representing X.\n" + \
        "  This represents one set of variables X, disjoint from Y.\n" + \
        "    Example: A, C, M\n" + \
        "  Input: "

    get_y_set_prompt = \
        "\nEnter a comma-separated list of variables, representing Y.\n" + \
        "  This represents one set of variables Y, disjoint from X.\n" + \
        "    Example: J, P\n" + \
        "  Input: "

    def __init__(self, graph: Graph):
        """
        Initializer for a BackdoorController
        :param graph: A Graph class used for traversal of the Causal Graph loaded
        """
        self.graph = graph

    def run(self):
        """
        Run one Backdoor session and exit
        """
        try:
            # Get X, Y sets and validate them
            x = self.get_variable_set(self.get_x_set_prompt)
            y = self.get_variable_set(self.get_y_set_prompt)

            assert len(x) > 0 and len(y) > 0, "Sets cannot be empty."
            assert len(x & y) == 0, "X and Y are not disjoint sets."
            for variable in x | y:
                assert variable in self.graph.v, "Variable " + variable + " not in the graph."

            # Calculate all the subsets possible
            valid_z_subsets = self.get_all_z_subsets(x, y)

            if len(valid_z_subsets) > 0:
                msg = "\nPossible sets Z that yield causal independence."
                for subset in valid_z_subsets:
                    msg += "\n  - " + "{" + ", ".join(item for item in subset) + "}"
                    msg += (" - Empty Set" if len(subset) == 0 else "")
                io.write(msg)
            else:
                io.write("\nNo possible set Z can be constructed to create causal independence.")

        except AssertionError as e:
            io.write(e.args)

    def get_all_z_subsets(self, x: set, y: set) -> list:
        """
        Finds all Z subsets that serve as deconfounding sets between X and Y
        :param x: Some set of variables X
        :param y: Some set of variables Y, which we want to find sets Z to give independence from X
        :return: A list of sets, each set representing a set of variables that are a sufficient Z set
        """

        # The cross product of X and Y
        cross_product = list(itertools.product(x, y))

        # Get the power set of all remaining variables, and check which subsets yield causal independence
        descendants_of_x = set().union(*[self.graph.reach(s) for s in x])
        disallowed_vertices = x | y | descendants_of_x
        z_power_set = power_set(set(self.graph.v) - disallowed_vertices)

        print(set(self.graph.v) - disallowed_vertices)
        # A set of all "eligible" subsets of the power set of the compliment of x|y|all_straight_line_path_variables;
        # any set in here is one which yields no backdoor backs from X x Y.
        valid_z_subsets = set()

        # Get the list of all backdoor paths detected in each subset
        for z_subset in z_power_set:

            # Tentative, indicating that no specific cross product in this subset has yet yielded any backdoor paths
            any_backdoor_paths = False

            # Cross represents one (x in X, y in Y) tuple
            for cross in cross_product:

                # Get any/all backdoor paths between this (x, y) and Z combination
                backdoor_paths = self.backdoor_paths(cross[0], cross[1], set(z_subset))

                # Debugging help
                # for path in backdoor_paths:
                #     print([str(item) for item in path])

                if len(backdoor_paths) > 0:
                    any_backdoor_paths = True
                    io.write_log(z_subset, "yields backdoor paths between", cross, end="")

                    for path in backdoor_paths:
                        msg = "  "
                        for index in range(len(path) - 1):
                            msg += path[index] + " "
                            msg += " <- " if path[index] in self.graph.children(path[index+1]) else " -> "
                        msg += path[-1]
                        io.write_log(msg)

                else:
                    io.write_log(z_subset, "yielded no backdoor paths for", cross, end="")

            # None found in any cross product -> Valid subset
            if not any_backdoor_paths:
                valid_z_subsets.add(z_subset)

        # Minimize the sets, if enabled
        if access("minimize_backdoor_sets"):
            valid_z_subsets = minimal_sets(valid_z_subsets)

        return list(valid_z_subsets)

    def any_backdoor_paths(self, x: set, y: set, z: set) -> bool:
        """
        Without seeing *which* paths are found, detect any backdoor paths between X and Y
        :param x: A set X, to be independent from Y
        :param y: A set Y, to be independent from X
        :param z: A set Z, to block paths between X and Y
        :return: True if there are any backdoor paths, False otherwise
        """
        for cross in itertools.product(x, y):
            if len(self.backdoor_paths(cross[0], cross[1], z)) > 0:
                return True
        return False

    def backdoor_paths(self, x: Variable, y: Variable, controlled_set: set):
        """
        :param x: The source Variable
        :param y: The target Variable
        :param controlled_set: A set of variables, Z, by which movement through any variable is controlled
        """

        def get_backdoor_paths(current: Variable, path: list, path_list: list, previous="up") -> list:
            """
            Return a list of lists of all paths from a source to a target, with conditional movement, child to parent.
            This is used in the detection of backdoor paths from Source to Target.
            This is a heavily modified version of the graph-traversal algorithm provided by Dr. Eric Neufeld.
            :param current: The current variable we will move away from
            :param path: The current path
            :param path_list: A list of lists, each sublist being a path
            :param previous: Whether moving from the previous variable to current we moved "up" (child to parent) or
                "down" (from parent to child); this movement restriction is involved in backdoor path detection
            :return: A list of lists, where each sublist is a backdoor path
            """

            def has_controlled_descendant(variable) -> bool:
                """
                :param variable: A Variable defined in the Causal Graph
                :return: True if Variable has at least one "controlled" descendant, which is in "controlled_set"
                """
                return any(var in controlled_set for var in self.graph.reach(variable))

            # Reached target
            if current == y:
                return path_list + [path + [y]]

            # No infinite loops
            if current not in path:

                if previous == "down":

                    # We can ascend on a controlled collider, OR an ancestor of a controlled collider
                    if current in controlled_set or has_controlled_descendant(current):
                        for parent in self.graph.parents(current):
                            path_list = get_backdoor_paths(parent, path + [current], path_list, "up")

                    # We can *continue* to descend on a non-controlled variable
                    if current not in controlled_set:
                        for child in self.graph.children(current):
                            path_list = get_backdoor_paths(child, path + [current], path_list, "down")

                if previous == "up":

                    if current not in controlled_set:

                        # We can ascend on a non-controlled variable
                        for parent in self.graph.parents(current):
                            path_list = get_backdoor_paths(parent, path + [current], path_list, "up")

                        # We can descend on a non-controlled reverse-collider
                        for child in self.graph.children(current):
                            path_list = get_backdoor_paths(child, path + [current], path_list, "down")

            return path_list

        # Get all possible backdoor paths
        self.graph.reset_disabled()
        backdoor_paths = get_backdoor_paths(x, [], [])

        # Filter out the paths that don't "enter" x; see the definition of a backdoor path
        filtered_paths = [path for path in backdoor_paths if path[0] in self.graph.children(path[1])]
        # filtered_paths = [path for path in filtered_paths if path[-1] in self.graph.children(path[-2])]
        return filtered_paths

    def all_paths_cumulative(self, source: str, target: str, path: list, path_list: list) -> list:
        """
        Return a list of lists of all paths from a source to a target, with conditional movement from child to parent.
        This is used in the detection of backdoor paths from Source to Target.
        This is a modified version of the graph-traversal algorithm provided by Dr. Eric Neufeld.
        :param source: The "source" Variable
        :param target: The "target"/destination Variable
        :param path: A current "path" of Variables seen along this traversal.
        :param path_list: A list which will contain lists of paths
        :return: A list of lists of Variables, where each sublist denotes a path from source to target
        """
        if source == target:
            return path_list + [path + [target]]
        if source not in path:
            for child in self.graph.children(source):
                path_list = self.all_paths_cumulative(child, target, path + [source], path_list)
        return path_list

    def get_variable_set(self, prompt: str) -> set:
        """
        Take a prompt to serve to the user and get a set of variables from the comma-separated response
        :param prompt:
        :return: A set processed from a comma-separated string of values, handling an empty string
        """
        input_set = set([item.strip() for item in input(prompt).split(",")])

        # Empty it if "enter" was the only thing given
        if input_set == {""}:
            input_set = set()
        return input_set

    def independent(self, x: set, y: set, z: set):
        """
        Helper function that makes some do_calculus logic more readable
        :param x: A set X, to be independent from Y
        :param y: A set Y, to be independent from X
        :param z: A set Z, to block paths between X and Y
        :return: True if there are no backdoor paths and no straight-line paths, False otherwise
        """
        # Not independent if there are any unblocked backdoor paths
        if self.any_backdoor_paths(x, y, z):
            return False

        # Ensure no straight-line variables from any X -> Y or Y -> X
        for cross in itertools.product(x, y):
            if len(self.all_paths_cumulative(cross[0], cross[1], [], [])) != 0:
                return False        # x -> y
            if len(self.all_paths_cumulative(cross[1], cross[0], [], [])) != 0:
                return False        # y -> x

        # No paths, must be independent
        return True
