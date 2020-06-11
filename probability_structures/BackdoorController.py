#########################################################
#                                                       #
#   BackdoorController                                  #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# The Outcome and Variable classes
from probability_structures.VariableStructures import Outcome, Variable


class BackdoorController:

    get_functionality_selection_prompt = \
        "\nSelect an option:\n" + \
        "    1) Find backdoor paths\n" + \
        "    2) Exit\n" + \
        "  Selection: "

    get_two_variables_prompt = \
        "\nEnter two variables to find backdoor paths between.\n" + \
        "  Give two, separated by commas.\n" + \
        "    Example: X, Y\n" + \
        "  Input: "

    get_controlled_variables_prompt = \
        "\nEnter variables being controlled for, in this query.\n" + \
        "  Give any number, separated by commas.\n" + \
        "    Example: X, Y, Z\n" + \
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

            # Clear the controlled variables on each run
            self.controlled = dict()
            for variable in self.variables:
                self.controlled[variable] = False

            # Get two variables to check for backdoor paths between
            try:
                split = [item.strip().upper() for item in input(self.get_two_variables_prompt).split(",")]
                assert len(split) == 2, "Too many variables."
                assert split[0] in self.variables and split[1] in self.variables
            except AssertionError:
                print("Some variable is not defined in this Causal Graph.")
                continue

            # Get control variables
            try:
                # Get optional controlled
                controlled = []
                controlled_preprocessed = input(self.get_controlled_variables_prompt).split(",")
                if controlled_preprocessed != ['']:
                    controlled = [item.strip().upper() for item in controlled_preprocessed]

                for control in controlled:
                    assert control in self.variables
                    self.controlled[control] = True
            except AssertionError:
                print("Some control variable is not defined in this Causal Graph.")
                continue

            body = self.variables[split[0]]
            head = self.variables[split[1]]

            # Swap the two given so that the order is correct, if X -> Y, and given Y, X, swap.
            if head.name in body.reach:
                body, head = head, body

            # Run query
            self.detect_paths(head, body)

            selection = input(self.get_functionality_selection_prompt)
            while selection not in ["1", "2"]:
                selection = input(self.get_functionality_selection_prompt)

            print()     # Some spacing for aesthetic

            if selection == "2":
                print("Exiting Backdoor Controller.")
                break

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



