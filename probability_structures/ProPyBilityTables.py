#########################################################
#                                                       #
#   ProPyBilityTables (Name is a work in progress)      #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Python libraries
import json             # Used to load tables/data
import numpy as np      # Used in table->str formatting
import math             # Used in table->str formatting
import argparse         # Allow command-line flag parsing

# Other modules of project
from probability_structures.ProbabilityExceptions import *      # Exceptions for Probability-computations
from probability_structures.VariableStructures import *         # The Outcome and Variable classes


class ConditionalProbabilityTable:
    """
    A basic conditional probability table that reflects the values of one Variable, and any number of conditional
    values

    :param variable: A Variable object, representing the variable this table computes a probability for
    :param given: A (possibly empty) list of Variables, representing the parents for the variable given
    :param table_rows: A list of rows in the table, each formatted as [<OUTCOME>, ["<GIVEN_1_OUTCOME>, ...], <P>]
    """

    # When outputting information, the number of digits to round to
    digits_of_probability_precision = 2

    # Padding units on the left/right sides of each cell
    padding = 1

    def __init__(self, variable: Variable, given: list, table_rows: list):
        self.variable = variable    # The LHS of the table, single-variable only
        self.given = given          # The RHS/body of the table

        self.table_rows = []

        # Clean up the rows; Each is formatted as: [outcome of variable, list of outcomes of parents, probability]
        for row in table_rows:
            self.table_rows.append([Outcome(variable.name, row[0]), row[1], float(row[2])])

    def __str__(self) -> str:
        """
        String builtin for a ConditionalProbabilityTable
        :return: A string representation of the table.
        """

        # Create a snazzy numpy table
        # Rows: 1 for a header + 1 for each row; Columns: 1 for variable, 1 for each given var, 1 for the probability
        rows = 1 + len(self.table_rows)
        columns = 1 + len(self.given) + 1

        # dtype declaration is better than "str", as str only allows one character in each cell
        table = np.empty((rows, columns), dtype='<U100')

        # Populate the first row: variable, given variables, probability
        table[0][0] = self.variable.name
        for i in range(len(self.given)):
            table[0][i+1] = self.given[i]
        table[0][table.shape[1]-1] = "P()"

        # Populate each row
        for i in range(len(self.table_rows)):

            row = self.table_rows[i]

            # Value of the given variable
            table[i+1][0] = row[0].outcome

            # Each given variable's value
            for given_idx in range(len(row[1])):
                table[i+1][1+given_idx] = row[1][given_idx]

            # The probability, to some modifiable number of digits
            table[i+1][table.shape[1]-1] = "{0:.2f}".format(row[2])

        # Wiggle/Padding, column by column
        for column_index in range(1 + len(self.given) + 1):
            widest_element = max([len(cell) for cell in table[:, column_index]])
            for row_index in range(1 + len(self.table_rows)):
                cell_value = table[row_index][column_index]
                l_padding = math.ceil((widest_element - len(cell_value) / 2)) * " " + " " * self.padding
                r_padding = math.floor((widest_element - len(cell_value) / 2)) * " " + " " * self.padding
                table[row_index][column_index] = l_padding + cell_value + r_padding

        # Convert to fancy string
        string_list = ["|" + "|".join(row) + "|" for row in table]
        top_bottom_wrap = "-" * len("|" + "|".join(table[0]) + "|")
        string_list.insert(1, top_bottom_wrap)

        return top_bottom_wrap + "\n" + "\n".join(string_list) + "\n" + top_bottom_wrap

    def __eq__(self, other) -> bool:
        """
        Equality builtin for a ConditionalProbabilityTable
        :param other: Another ConditionalProbabilityTable to compare to
        :return:
        """
        if isinstance(other, ConditionalProbabilityTable):
            return self.variable == other.variable and set(self.given) == set(other.given)
        else:
            return False

    def probability_lookup(self, outcome: list, given: set) -> float:
        """
        Directly lookup the probability for the row corresponding to the queried outcome and given data
        :param outcome: The specific outcome to lookup
        :param given: A set of [<VARIABLE>, <OUTCOME>] sub-lists of known data
        :return: A probability corresponding to the respective row. Raises an Exception otherwise.
        """
        for row in self.table_rows:
            # If the outcome for this row matches, and each outcome for the given data matches...
            if outcome[0] == row[0] and set(row[1]) == given:
                return row[2]       # We have our answer

        # Iterated over all the rows and didn't find the correct one
        raise Exception


class CausalGraph:
    """
    A "main" class driving most of the I/O
    """

    functionality_choice_prompt = \
        "\nSelect:" + \
        "\n    1) Compute a probability. Ex: P(X | Y)" + \
        "\n    2) Detect (and control) for \"back-door paths\"." + \
        "\n    3) Exit" + \
        "\n  Query: "

    get_specific_outcome_prompt =  \
        "\nQuery a specific variable and its outcome." + \
        "\n  Format as: <VARIABLE> = <OUTCOME>" + \
        "\n    Example: 'Y = ~y'" + \
        "\n  Query: "

    get_given_data_prompt = \
        "\nEnter the given variables for the query, as a comma-separated list." + \
        "\n  Format: '<VARIABLE_1> = <OUTCOME_1>, <VARIABLE_2> = <OUTCOME_2>'" + \
        "\n  Leave empty to not assert any 'given' data." + \
        "\n    Example: 'X = ~x, Z = z'" + \
        "\n  Query: "

    default_file_location = "causal_graph.json"

    # Toggle whether to suppress the computation output when computing probabilities
    #   Pass in a "-s" to turn this on, and only output conclusions
    silent_computation = False

    def __init__(self, filename=None):

        self.variables = dict()       # Maps string name to the Variable object instantiated
        self.tables = dict()          # Maps string name *and* corresponding variable to a list of corresponding tables
        self.outcomes = dict()        # Maps string name *and* corresponding variable to a list of outcome values

        self.determination = dict()

        # Maps string name *and* corresponding variable to a function used to determine its value
        self.functions = dict()

        # Allow a specified file location
        if filename is None:
            filename = self.default_file_location

        # Load the file, then we parse it
        with open(filename) as json_file:
            loaded_file = json.load(json_file)

        for variable in loaded_file["variables"]:

            name = variable["name"]
            outcomes = variable["outcomes"]
            parents = variable["parents"]

            # Create a fancy Variable object
            var = Variable(name, outcomes, parents)

            # Lookup the object by its name
            self.variables[variable["name"]] = var

            # Store by both the Variable object as well as its name, for ease of access
            self.outcomes[name] = variable["outcomes"]
            self.outcomes[var] = variable["outcomes"]

            # Is the variable determined by a function or direct tables?
            determination = variable["determination"]
            determination_type = determination["type"]

            if determination["type"] == "table":

                self.determination[name] = "table"
                self.determination[var] = "table"

                # Load in all the tables
                for table in determination["tables"]:

                    # Dictionary "tables" maps a variable/name to all the tables that show its probabilities
                    if name not in self.tables:
                        self.tables[name] = []
                        self.tables[self.variables[name]] = []

                    cpt = ConditionalProbabilityTable(self.variables[name], table["given"], table["rows"])

                    self.tables[name].append(cpt)
                    self.tables[self.variables[name]].append(cpt)

            elif determination_type == "function":

                self.determination[name] = "function"
                self.determination[var] = "function"

                self.functions[name] = determination["function"]
                self.functions[variable] = determination["function"]

            else:
                print("ERROR; Variable", name, "determination cannot be found.")
                exit(-1)

        # Reach initialization through recursive parent reverse-reach
        def reach_initialization(current: Variable, reachable_children: set):
            """
            Helper function to initialize the "reach" of each variable in the CG.
            :param current: A Variable to add the given children to the set of "reachable"s
            :param reachable_children: A set of string values of variables representing reachable children
            """
            current.reach.update(reachable_children)
            for parent in current.parents:
                reach_initialization(self.variables[parent], reachable_children.union({current.name}))

        # Call recursive initializer *from* each variable
        for variable in self.variables:
            reach_initialization(self.variables[variable], set())

        # Print all the variables out with their reach
        for variable in self.variables:
            print(str(self.variables[variable]), "; Reaches:", self.variables[variable].reach)

        parser = argparse.ArgumentParser(description="Compute probabilities.")
        parser.add_argument("-s", help="Silent computation; only show resulting probabilities.", action="store_true")
        options = parser.parse_args()
        if options.s:
            self.silent_computation = True

    def run(self):
        """
        The main REPL area of the project.
        """

        while True:

            # Get a selection from the user
            selection = input(self.functionality_choice_prompt).strip()
            while selection not in ["1", "2", "3"]:
                selection = input(self.functionality_choice_prompt).strip()

            # Compute a probability
            if selection == "1":
                self.setup_probability_computation()
            # We modify the graph heavily in backdoor-controlling, so I want to copy the graph and
            #   make such changes, so it's easiest to go make this its own "space".
            elif selection == "2":
                self.setup_backdoor_controller()
            elif selection == "3":
                print("Exiting.")
                exit(0)

    def setup_probability_computation(self):
        """
        Helper that gets data necessary to query a probability.
        """

        # Need an outcome to query, not necessarily any given data though
        outcome = []
        outcome_preprocessed = input(self.get_specific_outcome_prompt).split(",")

        try:
            for out in outcome_preprocessed:
                outcome_split = [var.strip() for var in out.split("=")]
                outcome.append(Outcome(outcome_split[0], outcome_split[1]))
        except IndexError:
            print("Improperly entered data.")
            return

        given_variables = []

        # Get optional "given" data and process it
        given_preprocessed = input(self.get_given_data_prompt).split(",")
        if given_preprocessed != ['']:
            try:
                for given in given_preprocessed:
                    given_split = [var.strip() for var in given.split("=")]
                    given_variables.append(Outcome(given_split[0], given_split[1]))
            except IndexError:
                print("Improperly entered data.")
                return

        print(self.p_str(outcome, given_variables))

        try:
            # Validate the queried variable and any given
            for out in outcome + given_variables:
                # Ensure variable is defined, outcome is possible for that variable, and it's formatted right.
                assert out.name in self.variables and out.outcome in self.outcomes[out.name]
        except AssertionError:
            print("The given data is incorrect:\n" +
                  " - Some outcome may not be possible for some variable\n" +
                  " - Some variable may not be defined")
            return

        try:
            probability = self.probability(outcome, given_variables)
            print("P = " + "{0:.2f}".format(probability))

        # Catch only exceptions for indeterminable queries
        #   We would still want other errors to come through
        except ProbabilityIndeterminableException:
            pass

    def setup_backdoor_controller(self):
        """
        Helper to setup and enter the backdoor controlling area
        """
        try:
            # Copy all the variables to avoid any issues
            copied_variables = dict()
            for variable_name in self.variables:
                copied_variables[variable_name] = self.variables[variable_name].copy()

            # Create and run a BackdoorController
            controller = BackdoorController(copied_variables)
            controller.run()  # Run the backdoor controller until closed

        except AssertionError:
            print("Error: Some variable given may not be defined")

    def has_table(self, name: str, given: set) -> bool:
        """
        Determine if the CausalGraph has a table corresponding to the given var|given variables
        :param name: The head/LHS of the query: "X" in P(X | Y)
        :param given: A set of Outcomes of the body/RHS of the query
        :return: True if there exists such a table, False otherwise
        """
        for table in self.tables[name]:
            if set(table.given) == set([outcome.name for outcome in given]):
                return True
        return False

    def get_table(self, name: str, given: set) -> ConditionalProbabilityTable or None:
        """
        Get a specific table given a variable, and a list of given data
        :param name: The variable being queried
        :param given: A list of string variables for which there is known values
        :return: A ConditionalProbabilityTable matching the above data if one exists, None otherwise
        """
        for table in self.tables[name]:
            if set(table.given) == set([outcome.name for outcome in given]):
                return table

    def p_str(self, lhs: list, rhs: list) -> str:
        """
        Convert a head&body to a properly-formatted string
        :param lhs: The head/LHS of the query
        :param rhs: The body/RHS of the query
        :return: A string representation "P(X | Y)"
        """
        string = "P(" + ", ".join([str(var) for var in lhs])
        if rhs:
            string += " | " + ", ".join([str(var) for var in rhs])
        return string + ")"

    def computation_output(self, *message: str, join=" ", end="\n"):
        """
        Optional output of any number of strings unless output is suppressed
        :param message: Any number of strings to print
        :param join: A string used to join the messages
        :param end: The end symbol outputted at the end of the series of strings
        :return:
        """
        if not self.silent_computation:
            for component in message:
                print(component, end=join)
            print(end=end)

    def probability(self, head: list, body: list, queries=None) -> float:
        """
        Compute the probability of some head given some body
        :param head: A list of some number of Outcome objects
        :param body: A list of some number of Outcome objects
        :param queries: A list of probabilities we are going down a DFS search to solve. Used to detect infinite loops.
        :return: A probability between [0.0, 1.0]
        """

        # Print the actual query being made on each recursive call to help follow
        self.computation_output("Trying:", self.p_str(head, body))

        # Keep a list of queries being passed through recursive calls to avoid infinite loops
        if queries is None:
            queries = []

        # If a string representation of this query is stored, we are in a loop and should stop
        if self.p_str(head, body) in queries:
            raise ProbabilityException

        # Create a copy and add the current string; we pass a copy to prevent issues with recursion
        new_queries = queries.copy() + [self.p_str(head, body)]

        ###############################################
        #            Single element on LHS            #
        ###############################################
        if len(head) == 1:

            ###############################################
            #         Attempt direct-table lookup         #
            ###############################################

            self.computation_output("\nQuerying table for: ", self.p_str(head, body))
            if self.has_table(head[0].name, set(body)):

                # Get the table
                table = self.get_table(head[0].name, set(body))
                self.computation_output(str(table))

                # Directly look up the corresponding row in the table
                #   Assumes a table has all combinations of values defined
                probability = table.probability_lookup(head, set([item.outcome for item in body]))
                self.computation_output(self.p_str(head, body), "=", probability)

                return probability
            else:
                self.computation_output("Not Found\n")

            ###############################################
            #                 Bayes' Rule                 #
            #      P(z | x) = P(x | z) * P(z) / P(x)      #
            ###############################################

            try:
                self.computation_output("Attempting application of Bayes' Rule")
                self.computation_output(self.p_str(head, body), "=", end=" ")
                self.computation_output(self.p_str(body, head), "*", self.p_str(head, []), "/", self.p_str(body, []))

                # flip flop flippy flop
                return self.probability(body, head, new_queries) * self.probability(head, [], new_queries) / self.probability(body, [], new_queries)
            except ProbabilityException:
                self.computation_output("Failed to resolve by Bayes'")

            ###############################################
            #        Eliminate non-parent ancestors       #
            ###############################################

            # A big list of Trues is created if body is all ancestors
            if False not in [head[0].name in self.variables[var.name].reach for var in body]:
                non_parent_ancestors = [anc for anc in body if anc.name not in self.variables[body[0].name].parents]
                for non_parent_ancestor in non_parent_ancestors:
                    try:
                        return self.probability(head, list(set(body) - {non_parent_ancestor}), new_queries)
                    except ProbabilityException:
                        print("Couldn't resolve by removing non-parent ancestors.")

        ##################################################################
        #   Easy identity rule; P(X | X) = 1, so if LHS ⊆ RHS, P = 1.0   #
        ##################################################################

        if set(head).issubset(set(body)):
            self.computation_output("Identity rule:", self.p_str(head, head), " = 1.0")
            self.computation_output("Therefore,", self.p_str(head, body), "= 1.0")
            return 1.0

        ###############################################
        #    Detect children of the LHS in the RHS    #
        #      p(a|Cd) = p(d|aC) p(a|C) / p(d|C)      #
        ###############################################

        reachable_from_head = set().union(*[self.variables[variable.name].reach for variable in head])
        children_in_rhs = set([var.name for var in body]) & reachable_from_head
        if len(children_in_rhs) > 0:

            self.computation_output("Children of the LHS in the RHS:", ",".join(children_in_rhs))
            try:
                # Not elegant, but simply take one of the children from the body out and recurse
                move = list(children_in_rhs).pop(0)
                move = [item for item in body if item.name == move]
                new_body = [variable for variable in body if variable != move[0]]

                self.computation_output(self.p_str(move, head + new_body), "*", self.p_str(head, new_body), "/", self.p_str(move, new_body)),

                return self.probability(move, head + new_body, new_queries) * self.probability(head, new_body, new_queries) / self.probability(move, new_body, new_queries)
            except ProbabilityException:
                pass

        ###############################################
        #                Jeffrey's Rule               #
        # P(y | x) = P(y | z, x) * P(z | x) + P(y | ~z, x) * P(~z | x) === sigma_Z P(y | z, x) * P(z | x)
        ###############################################

        # TODO - Try checking each of the values in head, not just the first
        missing_parents = self.missing_parents(head[0].name, set([parent.name for parent in body] + [parent.name for parent in head]))
        if missing_parents:
            self.computation_output("Attempting application of Jeffrey's Rule")

            # Try an approach beginning with each missing parent
            for missing_parent in missing_parents:

                try:
                    # Add one parent back in and recurse
                    add_parent = self.variables[missing_parent]

                    # Consider the missing parent and sum every probability involving it
                    total = 0.0
                    for parent_outcome in add_parent.outcomes:
                        as_outcome = Outcome(add_parent.name, parent_outcome)

                        self.computation_output(self.p_str(head, [as_outcome] + body), "*", end=" ")
                        self.computation_output(self.p_str([as_outcome], body))

                        total += self.probability(head, [as_outcome] + body, new_queries) * self.probability([as_outcome], body, new_queries)
                    return total

                except ProbabilityException:
                    self.computation_output("Failed to resolve by Jeffrey's Rule")

        ###############################################
        #             Reverse product rule            #
        #   P(y, x | ~z) = P(y | x, ~z) * P(x | ~z)   #
        ###############################################

        if len(head) > 1:
            try:
                return self.probability(head[:-1], [head[-1]] + body, new_queries) * self.probability([head[-1]], body, new_queries)
            except ProbabilityException:
                self.computation_output("Failed to resolve by reverse product rule.")

        ###############################################
        #               Cannot compute                #
        ###############################################

        raise ProbabilityIndeterminableException

    def missing_parents(self, variable: str or Variable, parent_subset: set) -> list:
        if isinstance(variable, str):
            return [parent for parent in self.variables[variable].parents if parent not in parent_subset]
        elif isinstance(variable, Variable):
            return [parent for parent in variable.parents if parent not in parent_subset]


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



