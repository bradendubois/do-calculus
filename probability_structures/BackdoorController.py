#########################################################
#                                                       #
#   BackdoorController                                  #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Python libraries
import itertools        # Used for power set / product creation

# The Variable class
from probability_structures.VariableStructures import Variable


def power_set(variable_list):
    """
    Quick helper that creates a chain of tuples, which will be the power set of the given list
    :param variable_list: A list of string variables
    :return: A chain object of tuples; power set of variable_list
    """
    p_set = list(variable_list)
    return itertools.chain.from_iterable(itertools.combinations(p_set, r) for r in range(len(p_set)+1))


class BackdoorController:

    get_functionality_selection_prompt = \
        "\nSelect an option:\n" + \
        "    1) Find backdoor paths\n" + \
        "    2) Exit\n" + \
        "  Selection: "

    get_x_set_prompt = \
        "\nEnter a comma-separated list of variables, representing X.\n" + \
        "  These must be in the causal graph, and will be independent from Y.\n" + \
        "    Example: A, C, M\n" + \
        "  Input: "

    get_y_set_prompt = \
        "\nEnter a comma-separated list of variables, representing Y.\n" + \
        "  These must be in the causal graph, and will be independent from X.\n" + \
        "    Example: J, P\n" + \
        "  Input: "

    get_z_set_prompt = \
        "\nEnter a comma-separated list of variables, representing Z.\n" + \
        "  These must be in the causal graph, and will be independent from X and Y.\n" + \
        "  These represent a set of controlled variables to ensure causal independence between X and Y." + \
        "    Example: E, N\n" + \
        "  Input: "

    def __init__(self, variables: dict):
        """
        Initializer for a BackdoorController
        :param variables: A dictionary of Variables (should be copied from the original CausalGraph, not a pointer to)
        """
        self.variables = variables

        # Utilize a dictionary to determine which variables are being controlled for; affects the path traversal used
        #   to identify backdoor paths
        self.controlled = dict()
        for variable in self.variables:
            self.controlled[variable] = False

        # Calculate all the children/outgoing of a variable. This representation shows the actual paths as in a causal
        #   diagram, but probability calculations really store edges going the opposite direction, child -> parent.

        # TODO - Can probably be done when a causal graph is created?
        self.children = dict()
        for variable in self.variables:
            if variable not in self.children:
                self.children[variable] = set()

            for parent in self.variables[variable].parents:
                if parent not in self.children:
                    self.children[parent] = set()
                self.children[parent].update(variable)

    def run(self):
        """
        Drives the IO of the BackdoorController
        """

        while True:

            try:
                # Get X, Y sets and validate them
                x = self.get_variable_set(self.get_x_set_prompt)
                y = self.get_variable_set(self.get_y_set_prompt)

                assert len(x) > 0 and len(y) > 0, "Sets cannot be empty."
                assert len(x & y) == 0, "X and Y are not disjoint sets."
                for variable in x | y:
                    assert variable in self.variables, "Variable " + variable + " not in the graph."

                # Calculate all the subsets possible
                valid_z_subsets = self.get_all_z_subsets(x, y)

                if len(valid_z_subsets) > 0:
                    print("\nPossible sets Z that yield causal independence.")
                    for subset in valid_z_subsets:
                        print("  -", "{" + ", ".join(item for item in subset) + "}" + (" - Empty Set" if len(subset) == 0 else ""))

                else:
                    print("\nNo possible set Z can be constructed to create causal independence.")

            except AssertionError as e:
                print(e.args)
                continue

            selection = input(self.get_functionality_selection_prompt)
            while selection not in ["1", "2"]:
                selection = input(self.get_functionality_selection_prompt)

            print()     # Some spacing for aesthetic

            if selection == "2":
                print("Exiting Backdoor Controller.")
                break

    def get_all_z_subsets(self, x: set, y: set) -> set:

        # Get the power set of all remaining variables, and check which subsets yield causal independence
        z_power_set = power_set(set(self.variables) - (x | y))

        # The cross product of X and Y
        cross_product = list(itertools.product(x, y))

        # A set of all "eligible" subsets of the power set of the compliment of x|y; any
        #   set in here is one which yields no backdoor backs from X x Y.
        valid_z_subsets = set()

        # Get the list of all backdoor paths detected in each subset
        for z_subset in z_power_set:

            # Tentative, indicating that no specific cross product has yet yielded any backdoor paths
            any_backdoor_paths = False

            # Cross represents one (x in X, y in Y) tuple
            for cross in cross_product:

                # Get any/all backdoor paths between this (x, y) and Z combination
                backdoor_paths = self.get_backdoor_paths(self.variables[cross[0]], self.variables[cross[1]], set(z_subset), [], [])

                # Debugging help
                # for path in backdoor_paths:
                #     print([str(item) for item in path])

                # Filter out the paths that don't "enter" x
                backdoor_paths = [path for path in backdoor_paths if path[1].name not in self.children[path[0].name]]

                # TODO - Toggle this output as a setting
                if len(backdoor_paths) > 0:
                    any_backdoor_paths = True

                    print("\n", z_subset, "yields backdoor paths between", cross)
                    for backdoor_path in backdoor_paths:
                        print("  ", end="")

                        for index in range(len(backdoor_path) - 1):
                            print(backdoor_path[index].name, end="")
                            print(" <- " if backdoor_path[index].name in self.children[backdoor_path[index + 1].name] else " -> ", end="")
                        print(backdoor_path[-1].name)
                    print()

                else:
                    print(z_subset, "yielded no backdoor paths for", cross)

            # None found in any cross product -> Valid subset
            if not any_backdoor_paths:
                valid_z_subsets.add(z_subset)

        # Return all the subsets
        return valid_z_subsets

    def get_variable_set(self, prompt: str) -> set:
        input_set = set([item.strip() for item in input(prompt).split(",")])

        # Empty it if "enter" was the only thing given
        if input_set == {""}:
            input_set = set()

        return input_set

    def get_backdoor_paths(self, x: Variable, y: Variable, controlled_set: set, path: list, path_list: list, previous="up") -> list:

        def has_controlled_descendant(variable: Variable):
            return any(var in controlled_set for var in variable.reach)

        if x == y:
            return path_list + [path + [y]]

        if x not in path:

            if previous == "down":

                # We can ascend on a controlled collider, OR an ancestor of a controlled collider
                if x.name in controlled_set or has_controlled_descendant(x):
                    for parent in x.parents:
                        path_list = self.get_backdoor_paths(self.variables[parent], y, controlled_set, path + [x], path_list, "up")

                # We can *continue* to descend on a non-controlled variable
                if x.name not in controlled_set:
                    for child in self.children[x.name]:
                        path_list = self.get_backdoor_paths(self.variables[child], y, controlled_set, path + [x], path_list, "down")

            if previous == "up":

                if x.name not in controlled_set:

                    # We can *continue* to descend on a non-controlled variable
                    for parent in x.parents:
                        path_list = self.get_backdoor_paths(self.variables[parent], y, controlled_set, path + [x], path_list, "up")

                    # We can descend on a non-controlled reverse-collider
                    for child in self.children[x.name]:
                        path_list = self.get_backdoor_paths(self.variables[child], y, controlled_set, path + [x], path_list, "down")

        return path_list

    # TODO - Rework into a boolean "any paths?" detector to improve testing?
    def detect_paths(self, head: Variable, body: Variable):

        # Find every path from the body to the head
        all_paths_to_body = self.all_paths_cumulative(head, body, [], [], True)
        found_one_backdoor = False

        for path in all_paths_to_body:

            # Note that this path is specifically a backdoor path, since it doesn't start by leaving through the body
            if path[1].name in head.parents:
                found_one_backdoor = True
                print("\nBackdoor: ", end="")
            else:
                print("Non-backdoor: ", end="")

            for index in range(len(path)-1):
                print(path[index].name, end="")
                print(" <- " if path[index].name in self.children[path[index+1].name] else " -> ", end="")
            print(path[-1].name)

        if not found_one_backdoor:
            print("No backdoor paths detected.")

    def all_paths_cumulative(self, source: Variable, target: Variable, path: list, path_list: list, can_ascend=True) -> list:
        """
        Return a list of lists of all paths from a source to a target, with conditional movement from child to parent.
        This is used in the detection of backdoor paths from Source to Target.
        This is a heavily modified version of the graph-traversal algorithm provided by Dr. Eric Neufeld.
        :param source: The "source" Variable
        :param target: The "target"/destination Variable
        :param path: A current "path" of Variables seen along this traversal.
        :param path_list: A list which will contain lists of paths
        :param can_ascend: Used as a flag to determine when we can attempt to traverse from child to parents
        :return: A list of lists of Variables, where each sublist denotes a path from source to target
        """
        if source == target:
            return path_list + [path + [target]]

        if source not in path:

            # If we can ascend (such as when we start from our source) or when we encounter a controlled collider
            if can_ascend or self.controlled[source.name] and not can_ascend:
                for parent in source.parents:
                    # Switch the flag to True since we can go up multiple child->parent levels once we start
                    path_list = self.all_paths_cumulative(self.variables[parent], target, path + [source], path_list, True)

            # Consider X <- A -> Y, if A is controlled, we can't go down it to reach X and Y
            if not self.controlled[source.name]:
                for neighbour in self.children[source.name]:
                    # Switch the flag to False, once going "down", can't go up until we reach a controlled collider
                    path_list = self.all_paths_cumulative(self.variables[neighbour], target, path + [source], path_list, False)

        return path_list



