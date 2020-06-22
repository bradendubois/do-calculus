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
import re               # Used in probabilistic function evaluation
import numpy as np      # Used in table->str formatting
import math             # Used in table->str formatting


# Other modules of project
from probability_structures.ProbabilityExceptions import *      # Exceptions for Probability-computations
from probability_structures.VariableStructures import *         # The Outcome and Variable classes
from config.config_manager import *
from probability_structures.BackdoorController import BackdoorController
from probability_structures.IO_Logger import *
from probability_structures.ConditionalProbabilityTable import ConditionalProbabilityTable


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

    get_probabilistic_variable_prompt = \
        "\nEnter a specific variable to compute the value of." + \
        "\n    Example: 'X'" + \
        "\n  Query: "

    def __init__(self, filename=None):

        self.variables = dict()       # Maps string name to the Variable object instantiated
        self.outcomes = dict()        # Maps string name *and* corresponding variable to a list of outcome values

        # All map a Variable object and its name to its respective value, if one exists
        self.determination = dict()   # Maps to "table" or "function", indicating how it is calculated
        self.tables = dict()          # Maps to corresponding tables
        self.functions = dict()       # Maps to corresponding functions

        # If enabled, stores a string representation of a query mapped to its result
        self.stored_computations = dict()

        # Allow a specified file location
        if filename is None:
            filename = access("graph_file_folder") + "/" + "causal_graph.json"

        # Ensure the file exists
        if not os.path.isfile(filename):
            io.write("ERROR: Can't find:", filename)
            exit(-1)

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
                io.write(str(self.variables[variable]), "; Reaches:", self.variables[variable].reach, end="")

        # "Startup"
        self.running = True

    def shutdown(self):
        self.running = False

    def run(self):
        """
        The main REPL area of the project.
        """

        while self.running:

            options = [
                # Compute a probability
                [self.setup_probability_computation, "Compute a probability. Ex: P(X | Y)"],

                # Compute some variable given that it has a function specified
                [self.setup_probabilistic_function, "Compute the value of a variable given some function. Ex: f(X) = 42"],

                # We modify the graph heavily in backdoor-controlling, so I want to copy the graph and
                #   make such changes, so it's easiest to go make this its own "space".
                [self.setup_backdoor_controller, "Detect (and control) for \"back-door paths\"."],

                # Exit back to the main IO controller
                [self.shutdown, "Exit / Switch Graph Files"]
            ]

            print("\n\nSelect:")
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
            # Open a file for logging
            io.open(self.p_str(outcome, given_variables))
            io.write("\n", self.p_str(outcome, given_variables) + "\n")

            # Compute the probability
            probability = self.probability(outcome, given_variables)

            # Log and close
            io.write("P = " + "{0:.{precision}f}".format(probability, precision=access("output_levels_of_precision")))
            io.close()

        # Catch only exceptions for indeterminable queries
        #   We would still want other errors to come through
        except ProbabilityIndeterminableException:
            pass

    def setup_probabilistic_function(self):

        try:
            # Get and verify variable is in the graph
            variable = input(self.get_probabilistic_variable_prompt).strip().upper()
            assert variable in self.variables

            # Calculate; results are a (min, max) tuple
            result = self.probabilistic_function_resolve(*self.functions[variable], apply_noise=access("apply_any_noise"))
            self.store_computation(str(variable), result)
            io.write(variable, "= min: {}, max: {}".format(*result))

        except AssertionError:
            print("Variable given not in the graph.")
        except NotFunctionDeterminableException:
            io.write("Variable is not resolvable by a probabilistic function.")

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

    def store_computation(self, string_representation: str, result: float or (float, float)):
        if access("cache_computation_results") and string_representation not in self.stored_computations:
            self.stored_computations[string_representation] = result

    def probabilistic_function_resolve(self, function: str, noise_function="", apply_noise=True, depth=0) -> (float, float):
        """
        Resolve a Variable, the value of which is determined by a probabilistic function
        :param function: The function to evaluate for a value
        :param noise_function: A noise function which, when evaluated, is applied to the original value
        :param apply_noise: Whether or not to apply any noise to the results
        :param depth: How many levels of recursion deep we are; used for output formatting
        :return: A float tuple (min, max) representing the range of values of the function
        """
        # Evaluate each var(foo) value, getting a min and max, and store these
        #   When we evaluate this function, we will take every possible cross product across
        #   the set of all resolved var(foo) values, ultimately returning the min and max
        nested_min_maxes = []

        # Split into segments and resolve each independently
        elements = function.split(" ")
        for element_idx in range(len(elements)):

            # A different probabilistic variable is involved, resolve it first
            if "val(" in elements[element_idx]:

                # The actual variable to be calculated
                trimmed = elements[element_idx].strip("val()")
                io.write("Evaluating value for:", trimmed, x_offset=depth)

                # Get the function/noise and calculate
                function_data = self.functions[trimmed]
                result = self.probabilistic_function_resolve(*function_data, apply_noise=access("recursive_noise_propagation"), depth=depth+1)

                # Store the (min, max) result, cache if desired
                nested_min_maxes.append(result)
                self.store_computation(trimmed, result)

                # Replace with a "{}" so that we can do some slick formatting for the main
                #   function evaluation later
                elements[element_idx] = "{}"

            # Probabilities are involved
            if "p(" in elements[element_idx]:

                # The variable to determine the probability of, split at the "|" if given into X | Y
                trimmed = elements[element_idx].strip("p()")
                split = re.split(r"\|", trimmed)

                # Create proper Outcome objects for everything
                head = [Outcome(*outcome.split("=")) for outcome in split[0].split(",")]
                body = []
                if len(split) == 2:
                    body = [Outcome(*outcome.split("=")) for outcome in split[1].split(",")]

                # Calculate the probability, substitute it into the original function
                result = self.probability(head, body, depth=depth+1)
                io.write(self.p_str(head, body), "=", str(result), x_offset=depth)
                elements[element_idx] = str(result)

        # All possible results, we will return the min and max to represent the range
        all_results = []

        # Rejoin each independently evaluated piece, evaluate in (what is now) basic arithmetic
        for cross in itertools.product(*nested_min_maxes):

            # Unpack a given cross-product across the string, substituted in anywhere we
            #   placed a "{}"
            result = eval(" ".join(elements).format(*cross))

            # Calculate and apply noise if given and enabled
            noise = 0
            if noise_function and apply_noise:
                print("Here", " ".join(elements).format(*cross))
                noise_range = self.probabilistic_function_resolve(noise_function, "", apply_noise=access("recursive_noise_propagation"), depth=depth+1)
                noise = sum(noise_range) / 2
            all_results.extend((result - noise, result + noise))

        result = min(all_results), max(all_results)
        io.write(function, "evaluates to", str(result))
        self.store_computation(function + noise_function, result)

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
        io.write("Trying:", self.p_str(head, body), x_offset=depth)

        # Keep a list of queries being passed through recursive calls to avoid infinite loops
        if queries is None:
            queries = []

        # If a string representation of this query is stored, we are in a loop and should stop
        if self.p_str(head, body) in queries:
            io.write("Already trying:", self.p_str(head, body), "returning.", x_offset=depth)
            raise ProbabilityException

        # If the calculation has been done and cached, just return it from storage
        if self.p_str(head, body) in self.stored_computations:
            result = self.stored_computations[self.p_str(head, body)]
            io.write("Computation already calculated:", self.p_str(head, body), "=", result, x_offset=depth)
            return result

        # If the calculation for this contains two separate outcomes for a variable (Y = y | Y = ~y), 0
        if self.contradictory_outcome_set(head + body):
            io.write("Two separate outcomes for one variable: 0.0")
            return 0.0

        # Create a copy and add the current string; we pass a copy to prevent issues with recursion
        new_queries = queries.copy() + [self.p_str(head, body)]

        ###############################################
        #         Attempt direct-table lookup         #
        ###############################################

        if len(head) == 1 and self.has_table(head[0].name, set(body)):

            io.write("\nQuerying table for: ", self.p_str(head, body), x_offset=depth)

            # Get the table
            table = self.get_table(head[0].name, set(body))
            io.write(str(table), x_offset=depth)

            # Directly look up the corresponding row in the table
            #   Assumes a table has all combinations of values defined
            probability = table.probability_lookup(head, set([item.outcome for item in body]))
            io.write(self.p_str(head, body), "=", probability, x_offset=depth)

            return probability
        else:
            io.write("Not Found\n", x_offset=depth)

        ###############################################
        #      Check for Function for Resolution      #
        ###############################################

        # TODO - Can probably remove? This should never happen and might be better handled with
        #   an exception rather than hope this will work out.
        if len(head) == 1 and self.determination[head[0].name] == "function":

            try:
                io.write("Attempting to resolve", head[0].name, "by a probabilistic function.")
                result = self.probabilistic_function_resolve(self.variables[head[0].name])
                self.store_computation(self.p_str(head, body), result)
                io.write(self.p_str(head, body), "=", str(result))
                return result
            except ProbabilityException:
                io.write("Couldn't resolve by a probabilistic function evaluation.")

        ##################################################################
        #   Easy identity rule; P(X | X) = 1, so if LHS ⊆ RHS, P = 1.0   #
        ##################################################################

        if set(head).issubset(set(body)):
            io.write("Identity rule:", self.p_str(head, head), " = 1.0", x_offset=depth)
            if len(head) > len(body):
                io.write("Therefore,", self.p_str(head, body), "= 1.0", x_offset=depth)
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
            io.write("Attempting application of Jeffrey's Rule", x_offset=depth)

            # Try an approach beginning with each missing parent
            for missing_parent in missing_parents:

                try:
                    # Add one parent back in and recurse
                    add_parent = self.variables[missing_parent]

                    # Consider the missing parent and sum every probability involving it
                    total = 0.0
                    for parent_outcome in add_parent.outcomes:

                        as_outcome = Outcome(add_parent.name, parent_outcome)

                        io.write(self.p_str(head, [as_outcome] + body), "*", self.p_str([as_outcome], body), end=" ", x_offset=depth)

                        result_1 = self.probability(head, [as_outcome] + body, new_queries, depth=depth + 1)
                        result_2 = self.probability([as_outcome], body, new_queries, depth + 1)
                        outcome_result = result_1 * result_2

                        total += outcome_result

                    self.store_computation(self.p_str(head, body), total)
                    return total

                except ProbabilityException:
                    io.write("Failed to resolve by Jeffrey's Rule", x_offset=depth)

        #################################################
        #     Detect children of the LHS in the RHS     #
        #      p(a|Cd) = p(d|aC) * p(a|C) / p(d|C)      #
        #################################################

        reachable_from_head = set().union(*[self.variables[variable.name].reach for variable in head])
        children_in_rhs = set([var.name for var in body]) & reachable_from_head
        if len(children_in_rhs) > 0:

            io.write("Children of the LHS in the RHS:", ",".join(children_in_rhs), x_offset=depth)
            try:
                # Not elegant, but simply take one of the children from the body out and recurse
                move = list(children_in_rhs).pop(0)
                move = [item for item in body if item.name == move]
                new_body = [variable for variable in body if variable != move[0]]

                str_1 = self.p_str(move, head + new_body)
                str_2 = self.p_str(head, new_body)
                str_3 = self.p_str(move, new_body)
                io.write(str_1, "*", str_2, "/", str_3, x_offset=depth)

                result_1 = self.probability(move, head + new_body, new_queries, depth + 1)
                result_2 = self.probability(head, new_body, new_queries, depth + 1)
                result_3 = self.probability(move, new_body, new_queries, depth + 1)

                result = result_1 * result_2 / result_3
                self.store_computation(self.p_str(head, body), result)
                return result

            except ProbabilityException:
                io.write("Failed to resolve by flipping")

        ###############################################
        #            Single element on LHS            #
        ###############################################

        if len(head) == 1 and not missing_parents and not reachable_from_head:

            ###############################################
            #                 Bayes' Rule                 #
            #      P(z | x) = P(x | z) * P(z) / P(x)      #
            ###############################################

            try:
                io.write("Attempting application of Bayes' Rule", x_offset=depth)
                io.write(self.p_str(head, body), "=", end=" ", x_offset=depth)
                io.write(self.p_str(body, head), "*", self.p_str(head, []), "/", self.p_str(body, []), x_offset=depth)

                # flip flop flippy flop
                result = self.probability(body, head, new_queries, depth + 1) * self.probability(head, [], new_queries, depth + 1) / self.probability(body, [], new_queries, depth + 1)
                self.store_computation(self.p_str(head, body), result)
                return result

            except ProbabilityException:
                io.write("Failed to resolve by Bayes'", x_offset=depth)

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
                        io.write("Couldn't resolve by removing non-parent ancestors.", x_offset=depth)

        ###############################################
        #             Reverse product rule            #
        #   P(y, x | ~z) = P(y | x, ~z) * P(x | ~z)   #
        ###############################################

        if len(head) > 1:
            try:
                return self.probability(head[:-1], [head[-1]] + body, new_queries, depth + 1) * self.probability([head[-1]], body, new_queries, depth + 1)
            except ProbabilityException:
                io.write("Failed to resolve by reverse product rule.", x_offset=depth)

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

