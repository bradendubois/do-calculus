#########################################################
#                                                       #
#   Causal Graph                                        #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Python libraries
import itertools
import json             # Used to load tables/data
import os               # Used to create a directory if not found
import re

import numpy as np      # Used in table->str formatting
import math             # Used in table->str formatting
import argparse         # Allow command-line flag parsing

# Other modules of project
from probability_structures.ProbabilityExceptions import *      # Exceptions for Probability-computations
from probability_structures.VariableStructures import *         # The Outcome and Variable classes
from config.config_mgr import *
from probability_structures.BackdoorController import BackdoorController


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

    def __init__(self, filename=None, silent_computation=False):

        self.variables = dict()       # Maps string name to the Variable object instantiated
        self.tables = dict()          # Maps string name *and* corresponding variable to a list of corresponding tables
        self.outcomes = dict()        # Maps string name *and* corresponding variable to a list of outcome values

        self.determination = dict() # Maybe unused as now

        self.store_computation_results = access("cache_computation_results")
        self.stored_computations = dict()

        self.open_write_file = None

        # Maps string name *and* corresponding variable to a function used to determine its value
        self.functions = dict()

        # Toggle whether to suppress the computation output when computing probabilities
        #   Pass in a "-s" to turn this on, and only output conclusions
        self.silent_computation = silent_computation

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
                self.functions[var] = determination["function"]

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
        if access("print_cg_info_on_instantiation"):
            for variable in self.variables:
                print(str(self.variables[variable]), "; Reaches:", self.variables[variable].reach)

    def run(self):
        """
        The main REPL area of the project.
        """

        while True:

            options = [
                # Compute a probability
                [self.setup_probability_computation, "Compute a probability. Ex: P(X | Y)"],
                # Compute some variable given that it has a function specified
                [self.setup_probabilistic_function, "Compute the value of a variable given some function. Ex: f(X) = 42"],
                # We modify the graph heavily in backdoor-controlling, so I want to copy the graph and
                #   make such changes, so it's easiest to go make this its own "space".
                [self.setup_backdoor_controller, "Detect (and control) for \"back-door paths\"."],
                [exit, "Exit"]
            ]

            print("\nSelect:")
            for option in range(len(options)):
                print("    " + str(option+1) + ") " + options[option][1])

            selection = input("\n  Query: ")
            while not selection.isdigit() or not 1 <= int(selection) <= len(options):
                selection = input("  Query: ")

            # Call the function corresponding to the selected option
            options[int(selection)-1][0]()

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

            if not os.path.isdir(access("logging_directory")):
                os.makedirs(access("logging_directory"))

            self.open_write_file = open(access("logging_directory") + "/" + self.p_str(outcome, given_variables), "w")
            probability = self.probability(outcome, given_variables)
            self.open_write_file.write(str(probability) + "\n")
            self.open_write_file.close()

            print("P = " + "{0:.{precision}f}".format(probability, precision=access("output_levels_of_precision")))

        # Catch only exceptions for indeterminable queries
        #   We would still want other errors to come through
        except ProbabilityIndeterminableException:
            pass

    def setup_probabilistic_function(self):
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

    def computation_output(self, *message: str, join=" ", end="\n", x_offset=0):
        """
        Optional output of any number of strings unless output is suppressed
        :param message: Any number of strings to print
        :param join: A string used to join the messages
        :param end: The end symbol outputted at the end of the series of strings
        :param x_offset: The amount of space at the beginning of every line to indent by
        :return:
        """

        indent = int(x_offset) * "  "

        if not self.silent_computation:
            print("\n" + indent, end="")

        if self.open_write_file:
            self.open_write_file.write("\n" + indent)

        for component in message:

            if not self.silent_computation:
                print(str(component).replace("\n", "\n" + indent, 100), end=join)

            if self.open_write_file:
                self.open_write_file.write(str(component).replace("\n",  "\n" + indent, 100) + join)

        if not self.silent_computation:
            print(end=end)

        if self.open_write_file:
            self.open_write_file.write(end)

    def store_computation(self, string_representation: str, probability: float):
        if self.store_computation_results and string_representation not in self.stored_computations:
            self.stored_computations[string_representation] = probability

    def probabilistic_function_resolve(self, var: Variable, depth=0) -> float:
        """
        Resolve a Variable, the value of which is determined by a probabilistic function
        :param var: The variable to find the value of
        :param depth: How many levels of recursion deep we are; used for output formatting
        :return: A float value (not necessarily in [0, 1.0] representing the value of var
        """

        # Quick check; ensure this variable actually has a "function"
        if self.determination[var] != "function":
            self.computation_output("Given", str(var), "is not resolvable by a probabilistic function!")
            raise Exception

        function: str
        function = self.functions[var.name]

        # Split into segments and resolve each independently
        elements = function.split(" ")
        for element_idx in range(len(elements)):

            # A different probabilistic variable is involved, resolve it first
            if "val(" in elements[element_idx]:
                trimmed = elements[element_idx].strip("val()")
                self.computation_output("Evaluating value for:", trimmed, x_offset=depth)
                result = self.probabilistic_function_resolve(self.variables[trimmed], depth+1)
                self.store_computation(trimmed, result)
                elements[element_idx] = str(result)

            # Some probabilities are involved
            if "p(" in elements[element_idx]:
                trimmed = elements[element_idx].strip("p()")
                split = re.split(r"\|", trimmed)

                head = [Outcome(*outcome.split("=")) for outcome in split[0].split(",")]
                body = []
                if len(split) == 2:
                    body = [Outcome(*outcome.split("=")) for outcome in split[1].split(",")]

                result = self.probability(head, body, depth=depth+1)
                self.computation_output(self.p_str(head, body), "=", str(result), x_offset=depth)
                self.store_computation(self.p_str(head, body), result)
                elements[element_idx] = str(result)

        # Rejoin each independently evaluated piece, evaluate in (what is now) basic arithmetic
        result = eval(" ".join(elements))
        self.computation_output(var.name, "evaluates to", str(result))
        self.store_computation(str(var), result)
        return result

    def probability(self, head: list, body: list, queries=None, depth=0) -> float:
        """
        Compute the probability of some head given some body
        :param head: A list of some number of Outcome objects
        :param body: A list of some number of Outcome objects
        :param queries: A list of probabilities we are going down a DFS search to solve. Used to detect infinite loops.
        :param depth: Used for horizontal offsets in outputting info
        :return: A probability between [0.0, 1.0]
        """

        # Print the actual query being made on each recursive call to help follow
        self.computation_output("Trying:", self.p_str(head, body), x_offset=depth)

        # Keep a list of queries being passed through recursive calls to avoid infinite loops
        if queries is None:
            queries = []

        # If a string representation of this query is stored, we are in a loop and should stop
        if self.p_str(head, body) in queries:
            self.computation_output("Already trying:", self.p_str(head, body), "returning.", x_offset=depth)
            raise ProbabilityException

        # If the calculation has been done and cached, just return it from storage
        if self.p_str(head, body) in self.stored_computations:
            result = self.stored_computations[self.p_str(head, body)]
            self.computation_output("Computation already calculated:", self.p_str(head, body), "=", result, x_offset=depth)
            return result

        # If the calculation for this contains two separate outcomes for a variable (Y = y | Y = ~y), 0
        if self.contradictory_outcome_set(head + body):
            self.computation_output("Two separate outcomes for one variable: 0.0")
            return 0.0

        # Create a copy and add the current string; we pass a copy to prevent issues with recursion
        new_queries = queries.copy() + [self.p_str(head, body)]

        ###############################################
        #         Attempt direct-table lookup         #
        ###############################################

        if len(head) == 1 and self.has_table(head[0].name, set(body)):

            self.computation_output("\nQuerying table for: ", self.p_str(head, body), x_offset=depth)

            # Get the table
            table = self.get_table(head[0].name, set(body))
            self.computation_output(str(table), x_offset=depth)

            # Directly look up the corresponding row in the table
            #   Assumes a table has all combinations of values defined
            probability = table.probability_lookup(head, set([item.outcome for item in body]))
            self.computation_output(self.p_str(head, body), "=", probability, x_offset=depth)

            return probability
        else:
            self.computation_output("Not Found\n", x_offset=depth)

        ###############################################
        #      Check for Function for Resolution      #
        ###############################################

        if len(head) == 1 and self.determination[head[0].name] == "function":

            try:
                self.computation_output("Attempting to resolve", head[0].name, "by a probabilistic function.")
                result = self.probabilistic_function_resolve(self.variables[head[0].name])
                self.store_computation(self.p_str(head, body), result)
                self.computation_output(self.p_str(head, body), "=", str(result))
                return result
            except ProbabilityException:
                self.computation_output("Couldn't resolve by a probabilistic function evaluation.")

        ##################################################################
        #   Easy identity rule; P(X | X) = 1, so if LHS ⊆ RHS, P = 1.0   #
        ##################################################################

        if set(head).issubset(set(body)):
            self.computation_output("Identity rule:", self.p_str(head, head), " = 1.0", x_offset=depth)
            if len(head) > len(body):
                self.computation_output("Therefore,", self.p_str(head, body), "= 1.0", x_offset=depth)
            return 1.0

        #######################################################################################################
        #                                            Jeffrey's Rule                                           #
        #   P(y | x) = P(y | z, x) * P(z | x) + P(y | ~z, x) * P(~z | x) === sigma_Z P(y | z, x) * P(z | x)   #
        #######################################################################################################

        # Detect all missing parents
        missing_parents = set()
        for outcome in head:
            missing_parents.update(self.missing_parents(outcome.name, set([parent.name for parent in head + body])))

        if missing_parents:
            self.computation_output("Attempting application of Jeffrey's Rule", x_offset=depth)

            # Try an approach beginning with each missing parent
            for missing_parent in missing_parents:

                try:
                    # Add one parent back in and recurse
                    add_parent = self.variables[missing_parent]

                    # Consider the missing parent and sum every probability involving it
                    total = 0.0
                    for parent_outcome in add_parent.outcomes:

                        as_outcome = Outcome(add_parent.name, parent_outcome)

                        self.computation_output(self.p_str(head, [as_outcome] + body), "*", self.p_str([as_outcome], body), end=" ", x_offset=depth)

                        result_1 = self.probability(head, [as_outcome] + body, new_queries, depth=depth + 1)
                        result_2 = self.probability([as_outcome], body, new_queries, depth + 1)
                        outcome_result = result_1 * result_2

                        total += outcome_result

                    self.store_computation(self.p_str(head, body), total)
                    return total

                except ProbabilityException:
                    self.computation_output("Failed to resolve by Jeffrey's Rule", x_offset=depth)

        #################################################
        #     Detect children of the LHS in the RHS     #
        #      p(a|Cd) = p(d|aC) * p(a|C) / p(d|C)      #
        #################################################

        reachable_from_head = set().union(*[self.variables[variable.name].reach for variable in head])
        children_in_rhs = set([var.name for var in body]) & reachable_from_head
        if len(children_in_rhs) > 0:

            self.computation_output("Children of the LHS in the RHS:", ",".join(children_in_rhs), x_offset=depth)
            try:
                # Not elegant, but simply take one of the children from the body out and recurse
                move = list(children_in_rhs).pop(0)
                move = [item for item in body if item.name == move]
                new_body = [variable for variable in body if variable != move[0]]

                str_1 = self.p_str(move, head + new_body)
                str_2 = self.p_str(head, new_body)
                str_3 = self.p_str(move, new_body)
                self.computation_output(str_1, "*", str_2, "/", str_3, x_offset=depth)

                result_1 = self.probability(move, head + new_body, new_queries, depth + 1)
                result_2 = self.probability(head, new_body, new_queries, depth + 1)
                result_3 = self.probability(move, new_body, new_queries, depth + 1)

                result = result_1 * result_2 / result_3
                self.store_computation(self.p_str(head, body), result)
                return result

            except ProbabilityException:
                self.computation_output("Failed to resolve by flipping")

        ###############################################
        #            Single element on LHS            #
        ###############################################

        if len(head) == 1 and not missing_parents and not reachable_from_head:

            ###############################################
            #                 Bayes' Rule                 #
            #      P(z | x) = P(x | z) * P(z) / P(x)      #
            ###############################################

            try:
                self.computation_output("Attempting application of Bayes' Rule", x_offset=depth)
                self.computation_output(self.p_str(head, body), "=", end=" ", x_offset=depth)
                self.computation_output(self.p_str(body, head), "*", self.p_str(head, []), "/", self.p_str(body, []), x_offset=depth)

                # flip flop flippy flop
                result = self.probability(body, head, new_queries, depth + 1) * self.probability(head, [], new_queries, depth + 1) / self.probability(body, [], new_queries, depth + 1)
                self.store_computation(self.p_str(head, body), result)
                return result

            except ProbabilityException:
                self.computation_output("Failed to resolve by Bayes'", x_offset=depth)

            ###############################################
            #        Eliminate non-parent ancestors       #
            ###############################################

            # A big list of Trues is created if body is all ancestors
            if False not in [head[0].name in self.variables[var.name].reach for var in body]:
                non_parent_ancestors = [anc for anc in body if anc.name not in self.variables[body[0].name].parents]
                for non_parent_ancestor in non_parent_ancestors:
                    try:
                        result = self.probability(head, list(set(body) - {non_parent_ancestor}), new_queries, depth + 1)
                        self.store_computation(self.p_str(head, body), result)
                        return result
                    except ProbabilityException:
                        self.computation_output("Couldn't resolve by removing non-parent ancestors.", x_offset=depth)

        ###############################################
        #             Reverse product rule            #
        #   P(y, x | ~z) = P(y | x, ~z) * P(x | ~z)   #
        ###############################################

        if len(head) > 1:
            try:
                return self.probability(head[:-1], [head[-1]] + body, new_queries, depth + 1) * self.probability([head[-1]], body, new_queries, depth + 1)
            except ProbabilityException:
                self.computation_output("Failed to resolve by reverse product rule.", x_offset=depth)

        ###############################################
        #               Cannot compute                #
        ###############################################

        raise ProbabilityIndeterminableException

    def contradictory_outcome_set(self, outcomes: list) -> bool:
        """
        Check whether a list of outcomes contain any contradictory values, such as Y = y and Y = ~y
        :param outcomes: A list of Outcome objects
        :return: True if there is a contradiction/implausibility, False otherwise
        """
        for cross in itertools.product(outcomes, outcomes):
            if cross[0].name == cross[1].name and cross[0].outcome != cross[1].outcome:
                return True
        return False

    def missing_parents(self, variable: str or Variable, parent_subset: set) -> list:
        """
        Get a list of all the missing parents of a variable
        :param variable: A variable object (either string or the object itself)
        :param parent_subset: A set of parent strings
        :return: The remaining parents of the given variable, as a list
        """
        if isinstance(variable, str):
            return [parent for parent in self.variables[variable].parents if parent not in parent_subset]
        elif isinstance(variable, Variable):
            return [parent for parent in variable.parents if parent not in parent_subset]
