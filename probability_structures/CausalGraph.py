#########################################################
#                                                       #
#   Causal Graph                                        #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

import itertools        # Used to create cross-products from iterables
import random           # Used to pick a random Z set in do-calculus
import operator         # Used to assist in sorting a list of Variables

from probability_structures.BackdoorController import BackdoorController
from probability_structures.ConditionalProbabilityTable import ConditionalProbabilityTable
from probability_structures.Graph import *
from probability_structures.VariableStructures import *
from utilities.IO_Logger import *
from utilities.ProbabilityExceptions import *


# Union all Variable types with string for functions that can take any of these
CG_Types = str or Variable or Outcome or Intervention


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

    error_msg_formatting = \
        "The given data is incorrect:\n" + \
        " - Some outcome may not be possible for some variable\n" + \
        " - Some variable may not be defined"

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
            outcomes = []
            if "outcomes" in variable:
                outcomes = variable["outcomes"]
            parents = variable["parents"]

            # Create a fancy Variable object
            var = Variable(name, outcomes, parents)

            # Lookup the object by its name
            self.variables[name] = var

            # Store by both the Variable object as well as its name, for ease of access
            self.outcomes[name] = outcomes
            self.outcomes[var] = outcomes

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

        def set_topological_ordering(current: Variable, depth=0):
            """
            Helper function to initialize the ordering of the Variables in the graph
            :param current: A Variable to set the ordering of, and then all its children
            :param depth: How many "levels deep"/variables traversed to reach current
            """
            current.topological_order = max(current.topological_order, depth)
            for child in [c for c in self.variables if current.name in self.variables[c].parents]:
                set_topological_ordering(self.variables[child], depth+1)

        # Begin the topological ordering, which is started from every "root" in the graph
        for root_node in [r for r in self.variables if len(self.variables[r].parents) == 0]:
            set_topological_ordering(self.variables[root_node])

        # Print all the variables out with their reach
        if access("print_cg_info_on_instantiation"):
            for variable in self.variables:
                io.write(str(self.variables[variable]), "; Reaches:", self.variables[variable].reach, "Order:", self.variables[variable].topological_order, end="")

        # Create the graph for queries
        v = set([v for v in self.variables])
        e = set().union(*[[(parent, child) for parent in self.variables[child].parents] for child in self.variables])
        self.graph = Graph(v, e)

        # Create a Backdoor Controller
        self.backdoor_controller = BackdoorController(self.variables)

        # "Startup"
        self.running = True

    def shutdown(self):
        self.running = False

    def run(self):
        """
        The main REPL area of the project.
        """

        self.running = True
        while self.running:

            # Start with base options of backdoor controlling and exiting
            options = [
                # We modify the graph heavily in backdoor-controlling, so I want to copy the graph and
                #   make such changes, so it's easiest to go make this its own "space".
                [self.backdoor_controller.run, "Detect (and control) for \"back-door paths\"."],

                # Pearl's Causality Text outlines 3 rules of do-calculus on pages 85-86
                [self.test_do_calculus_rules, "Apply and test the 3 rules of do-calculus."],

                # Generate a joint distribution table for the loaded graph
                [self.generate_joint_distribution_table, "Generate a joint distribution table."],

                # See the topological sorting of the graph
                [self.generate_topological_sort, "See a topological sorting of the graph."],

                # Exit back to the main IO controller
                [self.shutdown, "Exit / Switch Graph Files"]
            ]

            # We can *add* these two options if they are applicable; i.e, no probability stuff if no tables!
            #   Just a nice quality-of-life / polish touch

            # Compute some variable given that it has a function specified
            if len(self.functions) > 0:
                options.insert(0, [self.setup_probabilistic_function,
                                   "Compute the value of a variable given some function. Ex: f(X) = 42"])

            # Compute some probability variable given that it has tables specified
            if len(self.tables) > 0:
                options.insert(0, [self.setup_probability_computation,
                                   "Compute a probability. Ex: P(X | Y)"])

            # Actually print the menu, constructed from "options"
            print("\n\nSelect:")
            for option in range(len(options)):
                print("    " + str(option+1) + ") " + options[option][1])

            # Repeatedly re-query until a valid selection is made
            selection = input("\n  Query: ")
            while not selection.isdigit() or not 1 <= int(selection) <= len(options):
                selection = input("  Query: ")

            # Call the function corresponding to the selected option
            options[int(selection)-1][0]()

    def setup_probability_computation(self):
        """
        Helper that gets data necessary to query a probability.
        """

        # Get our input data first
        try:
            # Need an outcome to query, not necessarily any given data though
            outcome_preprocessed = input(self.get_specific_outcome_prompt)
            assert outcome_preprocessed != "", "No query being made; the head should not be empty."
            outcome = parse_outcomes_and_interventions(outcome_preprocessed)
            for out in outcome:     # Ensure there are no adjustments in the head
                assert not isinstance(out, Intervention), "Don't put adjustments in the head."

            # Get optional "given" data and process it
            given = []
            given_preprocessed = input(self.get_given_data_prompt)
            if given_preprocessed != "":
                given = parse_outcomes_and_interventions(given_preprocessed)

            # Validate the queried variable and any given
            for out in outcome + given:
                # Ensure variable is defined, outcome is possible for that variable, and it's formatted right.
                assert out.name in self.variables and out.outcome in self.outcomes[out.name], self.error_msg_formatting

        except AssertionError as e:
            io.write("Error: " + str(e.args), console_override=True)
            return

        except IndexError:
            io.write("Improperly entered data.", console_override=True)
            return

        str_rep = self.p_str(outcome, given)
        io.write("Query:", str_rep, console_override=True)

        try:
            # Open a file for logging
            io.open(self.p_str(outcome, given))
            io.write(self.p_str(outcome, given) + "\n")

            # If we have an Intervention in given, we need to construct Z
            # Then, we take set Z and take Sigma_Z P(Y | do(X)) * P(Z)
            if any(isinstance(g, Intervention) for g in given):
                x = set([x.name for x in outcome])
                y = set([y.name for y in given if isinstance(y, Intervention)])
                deconfounding_sets = BackdoorController(self.variables).get_all_z_subsets(y, x)

                # Filter out our Z sets with observations in them and verify there are still sets Z
                deconfounding_sets = [s for s in deconfounding_sets if not any(g.name in s for g in given if not isinstance(g, Intervention))]
                assert len(deconfounding_sets) > 0, "No deconfounding set Z can exist for the given data."

                self.graph.disable_incoming(*[var for var in given if isinstance(var, Intervention)])
                probability = self.handle_intervention_computation(outcome, given, deconfounding_sets)
                self.graph.reset_disabled()

            # Otherwise, compute the probability of a standard query
            else:
                probability = self.probability(outcome, given)

            # Log and close
            result = str_rep + " = {0:.{precision}f}".format(probability, precision=access("output_levels_of_precision"))
            io.write(result, console_override=True)
            io.close()

        # Catch only exceptions for indeterminable queries
        #   We would still want other errors to come through
        except ProbabilityIndeterminableException:
            pass

        except AssertionError as e:
            io.write(str(e.args), console_override=True)

    def handle_intervention_computation(self, outcome: list, given: list, deconfounding_sets: list) -> float:
        """
        Our "given" includes an Intervention/do(X); choose Z set(s) and return the probability of this do-calculus
        :param outcome: A list of Outcomes
        :param given: A list of Outcomes and/or Interventions
        :param deconfounding_sets: A list of sets, each a sufficient Z
        :return: A probability between 0 and 1 representing the probability of the query given some chosen Z set(s)
        """

        def single_z_set_run(given_set) -> float:
            """
            Compute a probability from the given x and y, with the given z as a deconfounder
            :param given_set: A specific set Z
            :return: A probability P, between 0.0 and 1.0
            """
            io.write("Choosing deconfounding set Z =", str(given_set))
            p = 0.0     # Start at 0

            # We take every possible combination of outcomes of Z and compute each probability separately
            for cross in itertools.product(*[self.outcomes[var] for var in given_set]):

                # Construct the respective Outcome list of each Z outcome cross product
                z_outcomes = []
                for cross_idx in range(len(given_set)):
                    z_outcomes.append(Outcome(list(given_set)[cross_idx], cross[cross_idx]))

                # First, we do our P(Y | do(X), Z)
                io.write("Computing sub-query: ", self.p_str(outcome, given + z_outcomes))
                p_y_x_z = self.probability(outcome, given + z_outcomes)
                # print(self.p_str(outcome, given + z_outcomes), "=", p_y_x_z)

                # Second, we do our P(Z)
                io.write("Computing sub-query: ", self.p_str(z_outcomes, given))
                p_z = self.probability(z_outcomes, [])
                # print(self.p_str(z_outcomes, []), "=", p_z)

                p += p_y_x_z * p_z      # Add to our total

            return p

        # How to choose the set Z; present them all and allow selection? Random? All?
        choose_z = access("z_selection_preference")

        # Try every possible Z; still return an answer, ensure only one unique answer is computed
        if choose_z == "all":

            # Sentinel value
            only_result = None
            io.write("Computing with every possible Z set.", console_override=True)

            # Use every possible set
            for z_set in deconfounding_sets:

                io.write("Computing with Z Set:", str(z_set))
                result = single_z_set_run(z_set)  # Compute with a specific set
                print(str(z_set), str(result))

                if only_result is None:  # Storing first result
                    only_result = result

                # If results do NOT match; error
                error_msg = "Error: Two distinct results from different Z sets: " + str(only_result) + "vs" + str(result)
                assert abs(result - only_result) < 0.00000001, error_msg

            probability = only_result

        # Randomly choose a set
        elif choose_z == "random":
            z_set = random.choice(deconfounding_sets)
            io.write("Choosing a set Z at random:", str(z_set), console_override=True)
            probability = single_z_set_run(z_set)

        # Present all sets and allow a choice to be made
        else:
            set_selection_prompt = "Select a deconfounding set:\n"
            for i in range(len(deconfounding_sets)):
                set_selection_prompt += "  " + str(i + 1) + ") " + str(deconfounding_sets[i]) + "\n"
            io.write(set_selection_prompt, end="", console_override=True)

            selection = input(" Selection: ")
            while not selection.isdigit() or not 1 <= int(selection) <= len(deconfounding_sets):
                selection = input(" Selection: ")

            selected_set = deconfounding_sets[int(selection) - 1]
            io.write("Set selected:", str(selected_set), console_override=True)
            probability = single_z_set_run(selected_set)

        return probability

    def setup_probabilistic_function(self):
        """
        Setup and execute a query of some variable which is determined by a function rather than probability tables
        """
        try:
            # Get and verify variable is in the graph
            variable = input(self.get_probabilistic_variable_prompt).strip()
            assert variable in self.variables

            # Calculate; results are a (min, max) tuple
            io.open("f(" + variable + ")")
            result = self.probabilistic_function_resolve(*self.functions[variable], apply_noise=access("apply_any_noise"))
            self.store_computation(str(variable), result)
            io.write(variable, "= min: {}, max: {}".format(*result), console_override=True)
            io.close()

        except KeyError:
            io.write("Given variable not resolvable by a probabilistic function.", console_override=True)
        except AssertionError:
            io.write("Variable given not in the graph.", console_override=True)

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
        # Create a string representation of the given query
        str_rep = function
        if noise_function:
            str_rep += " +- " + noise_function

        # Check if we cached the result already
        if str_rep in self.stored_computations:
            io.write(str_rep, "already computed.", x_offset=depth)
            return self.stored_computations[str_rep]

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

                # Replace with a "{}" so that we can do some slick formatting for the main function evaluation later
                elements[element_idx] = "{}"

            # Probabilities are involved
            if "p(" in elements[element_idx]:

                # The variable to determine the probability of, split at the "|" if given into X | Y
                trimmed = elements[element_idx].strip("p()")
                split = re.split(r"\|", trimmed)

                # Create proper Outcome objects for everything
                head = parse_outcomes_and_interventions(split[0])
                body = []
                if len(split) == 2:
                    body = parse_outcomes_and_interventions(split[1])

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
                noise_range = self.probabilistic_function_resolve(noise_function, "", apply_noise=access("recursive_noise_propagation"), depth=depth+1)
                noise = sum(noise_range) / 2
            all_results.extend((result - noise, result + noise))

        result = min(all_results), max(all_results)
        io.write(function, "evaluates to", str(result), x_offset=depth)
        self.store_computation(str_rep, result)

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
        ###############################################
        #   Begin with bookkeeping / error-checking   #
        ###############################################

        # Sort the head and body if enabled
        if access("topological_sort_variables"):
            head, body = self.descendant_first_sort(head), self.descendant_first_sort(body)

        # Create a string representation of this query, and see if it's been done / in-progress / contradictory
        str_rep = self.p_str(head, body)

        # Print the actual query being made on each recursive call to help follow
        io.write("Querying:", str_rep, x_offset=depth)

        # Keep a list of queries being passed through recursive calls to avoid infinite loops
        if queries is None:
            queries = []

        # If a string representation of this query is stored, we are in a loop and should stop
        # NOTE - This never occurs anymore as improvements have been made.
        if str_rep in queries:
            io.write("Already trying:", str_rep, "returning.", x_offset=depth)
            raise ProbabilityException

        # If the calculation has been done and cached, just return it from storage
        if str_rep in self.stored_computations:
            result = self.stored_computations[str_rep]
            io.write("Computation already calculated:", str_rep, "=", result, x_offset=depth)
            return result

        # If the calculation for this contains two separate outcomes for a variable (Y = y | Y = ~y), 0
        if self.contradictory_outcome_set(head + body):
            io.write("Two separate outcomes for one variable: 0.0")
            return 0.0

        # Check for Function for Resolution
        if len(head) == 1 and self.determination[head[0].name] == "function":
            io.write("Couldn't resolve by a probabilistic function evaluation.")
            raise ProbabilityException

        # Create a copy and add the current string; we pass a copy to prevent issues with recursion
        new_queries = queries.copy() + [str_rep]

        ###############################################
        #             Reverse product rule            #
        #   P(y, x | ~z) = P(y | x, ~z) * P(x | ~z)   #
        ###############################################

        if len(head) > 1:
            try:
                io.write("Applying reverse product rule to", str_rep)

                result_1 = self.probability(head[:-1], [head[-1]] + body, new_queries, depth+1)
                result_2 = self.probability([head[-1]], body, new_queries, depth+1)
                result = result_1 * result_2

                io.write(str_rep, "=", str(result), x_offset=depth)
                self.store_computation(str_rep, result)
                return result
            except ProbabilityException:
                io.write("Failed to resolve by reverse product rule.", x_offset=depth)

        ###############################################
        #            Attempt direct lookup            #
        ###############################################

        if len(head) == 1 and self.has_table(head[0].name, set(body)):

            io.write("Querying table for: ", self.p_str(head, body), x_offset=depth, end="")
            table = self.get_table(head[0].name, set(body))         # Get table
            io.write(str(table), x_offset=depth, end="")            # Show table
            probability = table.probability_lookup(head, body)      # Get specific row
            io.write(self.p_str(head, body), "=", probability, x_offset=depth)

            return probability
        else:
            io.write("No direct table found.", x_offset=depth)

        ##################################################################
        #   Easy identity rule; P(X | X) = 1, so if LHS ⊆ RHS, P = 1.0   #
        ##################################################################

        if set(head).issubset(set(body)):
            io.write("Identity rule:", self.p_str(head, head), " = 1.0", x_offset=depth)
            if len(head) > len(body):
                io.write("Therefore,", self.p_str(head, body), "= 1.0", x_offset=depth)
            return 1.0

        #################################################
        #                  Bayes' Rule                  #
        #     Detect children of the LHS in the RHS     #
        #      p(a|Cd) = p(d|aC) * p(a|C) / p(d|C)      #
        #################################################

        reachable_from_head = set().union(*[self.graph.full_reach(outcome) for outcome in head])
        descendants_in_rhs = set([var.name for var in body]) & reachable_from_head

        if descendants_in_rhs:
            io.write("Children of the LHS in the RHS:", ",".join(descendants_in_rhs), x_offset=depth, end="")
            io.write("Applying Bayes' rule.", x_offset=depth)

            try:
                # Not elegant, but simply take one of the children from the body out and recurse
                child = list(descendants_in_rhs).pop(0)
                child = [item for item in body if item.name == child]
                new_body = list(set(body) - set(child))

                str_1 = self.p_str(child, head + new_body)
                str_2 = self.p_str(head, new_body)
                str_3 = self.p_str(child, new_body)
                io.write(str_1, "*", str_2, "/", str_3, x_offset=depth)

                result_1 = self.probability(child, head + new_body, new_queries, depth + 1)
                result_2 = self.probability(head, new_body, new_queries, depth + 1)
                result_3 = self.probability(child, new_body, new_queries, depth + 1)
                if result_3 == 0:
                    io.write(str_3, "= 0, therefore the result is 0.", x_offset=depth)
                    return 0

                # flip flop flippy flop
                result = result_1 * result_2 / result_3
                io.write(str_rep, "=", str(result), x_offset=depth)
                self.store_computation(str_rep, result)
                return result

            except ProbabilityException:
                io.write("Failed to resolve by Bayes", x_offset=depth)

        #######################################################################################################
        #                                  Jeffrey's Rule / Distributive Rule                                 #
        #   P(y | x) = P(y | z, x) * P(z | x) + P(y | ~z, x) * P(~z | x) === sigma_Z P(y | z, x) * P(z | x)   #
        #######################################################################################################

        missing_parents = set()
        for outcome in head:
            missing_parents.update(self.missing_parents(outcome, set([parent.name for parent in head + body])))

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

                        io.write(self.p_str(head, [as_outcome] + body), "*", self.p_str([as_outcome], body), x_offset=depth)

                        result_1 = self.probability(head, [as_outcome] + body, new_queries, depth=depth + 1)
                        result_2 = self.probability([as_outcome], body, new_queries, depth=depth+1)
                        outcome_result = result_1 * result_2

                        total += outcome_result

                    io.write(str_rep, "=", str(total), x_offset=depth)
                    self.store_computation(str_rep, total)
                    return total

                except ProbabilityException:
                    io.write("Failed to resolve by Jeffrey's Rule", x_offset=depth)

        ###############################################
        #            Interventions / do(X)            #
        ###############################################

        # Interventions imply that we have fixed X=x
        if isinstance(head[0], Intervention) and len(head) == 1 and not descendants_in_rhs:
            io.write("Intervention without RHS Children:", str_rep, "= 1.0", x_offset=depth)
            return 1.0

        ###############################################
        #            Single element on LHS            #
        #               Drop non-parents              #
        ###############################################

        if len(head) == 1 and not missing_parents and not descendants_in_rhs:

            head_var = self.variables[head[0].name]
            can_drop = [var for var in body if var.name not in head_var.parents]

            if can_drop:
                try:
                    io.write("Can drop:", str([str(item) for item in can_drop]), x_offset=depth)
                    result = self.probability(head, list(set(body) - set(can_drop)), new_queries, depth+1)
                    io.write(str_rep, "=", str(result), x_offset=depth)
                    self.store_computation(str_rep, result)
                    return result

                except ProbabilityException:
                    pass

        ###############################################
        #               Cannot compute                #
        ###############################################

        raise ProbabilityIndeterminableException

    def generate_joint_distribution_table(self):
        """
        Generate and present a joint distribution table for the loaded graph.
        """
        # First, lets sort the variables for some nice presentation
        sort_keys = sorted(self.variables.keys())

        # Get all the possible outcomes for each respective variable, stored as a list of lists, ordered mirroring keys
        sorted_outcomes = [self.variables[key].outcomes for key in sort_keys]

        results = []

        # Cross product of this list and calculate each probability
        for cross in itertools.product(*sorted_outcomes):

            # Construct each Outcome by pairing the sorted keys with the outcome chosen
            outcomes = [Outcome(sort_keys[i], cross[i]) for i in range(len(sort_keys))]
            result = self.probability(outcomes, [])
            results.append([",".join(cross), [], result])

        results.append(["Total:", [], sum(r[2] for r in results)])

        # Create the table, then print it (with some aesthetic offsetting)
        cpt = ConditionalProbabilityTable(Variable(",".join(sort_keys), [], []), [], results)
        io.write("Joint Distribution Table for: " + ",".join(sort_keys), "\n", str(cpt), x_offset=1, console_override=True)

    def generate_topological_sort(self):
        """
        Generate and present a topological sorting of the graph
        """
        maximum_depth = max(self.variables[v].topological_order for v in self.variables)
        io.write("*** Topological Sort ***", end="", console_override=True)
        for depth in range(maximum_depth):
            this_depth = [self.variables[item].name for item in self.variables if self.variables[item].topological_order == depth]
            io.write("Depth", str(depth) + ":", ", ".join(sorted(this_depth)), end="", console_override=True)

    def missing_parents(self, variable: CG_Types, parent_subset: set) -> list:
        """
        Get a list of all the missing parents of a variable
        :param variable: A variable object (either string or the object itself) or an Outcome
        :param parent_subset: A set of parent strings
        :return: The remaining parents of the given variable, as a list
        """
        return list(self.graph.parents(variable) - parent_subset)

    def variable_sort(self, variables: list) -> list:
        """
        A helper function to abstract what it means to "sort" a list of Variables/Outcomes/Interventions
        :param variables: A list of any number of Variable/Outcome/Intervention instances
        :return: A list, sorted (currently in the form of a topological sort)
        """
        # No matter what type of item is in the list, take its name (all have one) and access the variables dict
        sorted_variables = sorted([self.variables[f.name] for f in variables], key=operator.attrgetter("topological_order"))
        sort_given = []
        sort_map = {item.name: item for item in variables}
        for s in sorted_variables:
            sort_given.append(sort_map[s.name])
        return sort_given

    def descendant_first_sort(self, variables: list) -> list:
        """
        A helper function to "sort" a list of Variables/Outcomes/Interventions such that no element has a
        "parent"/"ancestor" to its left
        :param variables: A list of any number of Variable/Outcome/Intervention instances
        :return: A sorted list, such that any instance has no ancestor earlier in the list
        """
        # We can already do top-down sorting, just reverse the answer
        return self.variable_sort(variables)[::-1]

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

    def test_do_calculus_rules(self):
        """
        Enter a smaller IO stage in which we take 4 sets (X, Y, W, Z) and see which of the 3 do-calculus rules apply.
        """

        do_calculus_prompt = "To test the 3 rules of do-calculus, we will need 4 sets of variables: X, Y, Z, and " \
                             "W.\nIn these rules, X and Z may be interventions. The rules are:\n" \
                             "Rule 1: P(y | do(x), z, w) = P(y | do(x), w) if (Y _||_ Z | X, W) in G(-X)\n" \
                             "Rule 2: P(y | do(x), do(z), w) = P(y | do(x), z, w) if (Y _||_ Z | X, W) in G(-X, Z_)\n" \
                             "Rule 3: P(y | do(x), do(z), w) = P(y | do(x), w) if (Y _||_ Z | X, W) in G(-X, -Z(W))"

