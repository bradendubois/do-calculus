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
from utilities.IterableIndexSelection import *
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

        # Ensure the file exists
        if not os.path.isfile(filename):
            io.write("ERROR: Can't find:", filename)
            raise Exception

        # Load the file, then we parse it
        with open(filename) as json_file:
            loaded_file = json.load(json_file)

        self.variables = dict()       # Maps string name to the Variable object instantiated
        self.outcomes = dict()        # Maps string name *and* corresponding variable to a list of outcome values

        # All map a Variable object and its name to its respective value, if one exists
        self.determination = dict()   # Maps to "table" or "function", indicating how it is calculated
        self.tables = dict()          # Maps to corresponding tables
        self.functions = dict()       # Maps to corresponding functions

        # If enabled, stores a string representation of a query mapped to its result
        self.stored_computations = dict()

        for v in loaded_file["variables"]:

            # Load the relevant data to construct a Variable
            name = v["name"]
            outcomes = v["outcomes"] if "outcomes" in v else []
            parents = v["parents"] if "parents" in v else []

            # Create a fancy Variable object
            variable = Variable(name, outcomes, parents)

            # Lookup the object by its name
            self.variables[name] = variable

            # Store by both the Variable object as well as its name, for ease of access
            self.outcomes[name] = outcomes
            self.outcomes[variable] = outcomes

            # Is the variable determined by a function or direct tables?
            determination = v["determination"]
            determination_type = determination["type"]

            if determination["type"] == "table":

                # Save that this variable is determined by a table
                self.determination[name] = "table"
                self.determination[variable] = "table"

                # Load in the table and construct a CPT
                table = determination["table"]
                cpt = ConditionalProbabilityTable(self.variables[name], table["given"], table["rows"])

                # Map the name/variable to the table
                self.tables[name] = cpt
                self.tables[self.variables[name]] = cpt

            elif determination_type == "function":

                # Save that this variable is determined by a function
                self.determination[name] = "function"
                self.determination[variable] = "function"

                # Map the name/variable to the function
                self.functions[name] = determination["function"]
                self.functions[variable] = determination["function"]

            else:
                print("ERROR; Variable", name, "determination cannot be found.")
                exit(-1)

        # Create a Backdoor Controller
        self.backdoor_controller = BackdoorController(self.variables)

        # Create the graph for queries
        v = set([v for v in self.variables])
        e = set().union(*[[(parent, child) for parent in self.variables[child].parents] for child in self.variables])
        self.graph = Graph(v, e)

        # Update the topological ordering (as specified by the graph) for later sorting purposes
        for variable in self.variables:
            self.variables[variable].topological_order = self.graph.get_topology(variable)

        # Print all the variables out with their reach
        show = access("print_cg_info_on_instantiation") and io.console_enabled
        for variable in self.variables:
            v = self.variables[variable]
            io.write(str(v), "; Reaches:", v.reach, "Order:", v.topological_order, end="", console_override=show)

        # Aesthetic spacing
        io.write(end="", console_override=show)

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
            menu_options = [
                [self.backdoor_controller.run, "Detect (and control) for \"back-door paths\"."],
                [self.test_do_calculus_rules, "Apply and test the 3 rules of do-calculus."],
                [self.generate_joint_distribution_table, "Generate a joint distribution table."],
                [self.generate_topological_sort, "See a topological sorting of the graph."],
                [self.shutdown, "Exit / Switch Graph Files"]
            ]

            # We *add* these two options if they are applicable; i.e, no probability stuff if no tables!

            # Compute some variable given that it has a function specified
            if len(self.functions) > 0:
                menu_options.insert(0, [self.setup_probabilistic_function,
                                        "Compute the value of a variable given some function. Ex: f(X) = 42"
                                        ])

            # Compute some probability variable given that it has tables specified
            if len(self.tables) > 0:
                menu_options.insert(0, [self.setup_probability_computation,
                                        "Compute a probability. Ex: P(X | Y)"
                                        ])

            # Construct the menu and get the user to select an option
            menu_selection = user_index_selection("Select an option:", menu_options)

            # Call the function corresponding to the selected option
            menu_options[menu_selection][0]()

    def setup_probability_computation(self):
        """
        Helper that gets data necessary to query a probability.
        """

        # Get our input data first
        try:
            # Need an outcome to query, not necessarily any given data though
            head_preprocessed = input(self.get_specific_outcome_prompt)
            assert head_preprocessed != "", "No query being made; the head should not be empty."
            head = parse_outcomes_and_interventions(head_preprocessed)
            for out in head:     # Ensure there are no adjustments in the head
                assert not isinstance(out, Intervention), "Don't put adjustments in the head."

            # Get optional "given" data and process it
            body = []
            body_preprocessed = input(self.get_given_data_prompt)
            if body_preprocessed != "":
                body = parse_outcomes_and_interventions(body_preprocessed)

            # Validate the queried variable and any given
            for out in head + body:
                # Ensure variable is defined, outcome is possible for that variable, and it's formatted right.
                assert out.name in self.variables and out.outcome in self.outcomes[out.name], self.error_msg_formatting

        except AssertionError as e:
            io.write("Error: " + str(e.args), console_override=True)
            return

        except IndexError:      # Happens if just given "X", not "X=x", making the Outcome() crash
            io.write("Improperly entered data.", console_override=True)
            return

        str_rep = self.p_str(head, body)
        io.write("Query:", str_rep, console_override=True)

        try:
            # Open a file for logging
            io.open(self.p_str(head, body))
            io.write(self.p_str(head, body), "\n")

            # If we have an Intervention in given, we need to construct Z
            # Then, we take set Z and take Sigma_Z P(Y | do(X)) * P(Z)
            if any(isinstance(g, Intervention) for g in body):
                x = set([x.name for x in head])
                y = set([y.name for y in body if isinstance(y, Intervention)])
                deconfounding_sets = BackdoorController(self.variables).get_all_z_subsets(y, x)

                # Filter out our Z sets with observations in them and verify there are still sets Z
                deconfounding_sets = [s for s in deconfounding_sets if not any(g.name in s for g in body if not isinstance(g, Intervention))]
                assert len(deconfounding_sets) > 0, "No deconfounding set Z can exist for the given data."

                self.graph.disable_incoming(*[var for var in body if isinstance(var, Intervention)])
                probability = self.handle_intervention_computation(head, body, deconfounding_sets)
                self.graph.reset_disabled()

            # Otherwise, compute the probability of a standard query
            else:
                probability = self.probability(head, body)

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

            selected = deconfounding_sets
            message = "Computing with every possible Z set."

        elif choose_z == "random":

            selected = random.choice(deconfounding_sets)
            message = "Choosing a set Z at random: " + str(selected)

        elif choose_z == "ask":

            # Generate a message to list all sets and ask for one to be selected
            set_selection = user_index_selection("Select a deconfounding set:", deconfounding_sets)
            selected = deconfounding_sets[set_selection]
            message = "Set selected: " + str(selected)

        else:
            raise Exception("Somehow the Z selection configuration is invalid.")

        io.write(message, console_override=True)

        # Handle the "all" case and individual case in one by iterating through the list of sets
        #   Just convert the single-set selections to a single-element list
        if not isinstance(selected, list):
            selected = [selected]

        only_result = None      # Sentinel value
        for z_set in selected:

            io.write("Computing with Z Set:", str(z_set))
            result = single_z_set_run(z_set)  # Compute with a specific set
            io.write(str(z_set), str(result), end="", console_override=True)

            if only_result is None:  # Storing first result
                only_result = result

            # If results do NOT match; error
            error_msg = "Error: Two distinct results from different Z sets: " + str(only_result) + "vs" + str(result)
            assert abs(result - only_result) < 0.00000001, error_msg

        return only_result

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
        """
        Store a computed result mapped by its query/representation, to speed up future queries
        :param string_representation: Whatever representation for this query: "P(Y | X)", etc.
        :param result: The actual value to store, float for probabilities, (float, float) for continuous
        """
        # Ensure the configuration file is specified to allow caching
        if access("cache_computation_results"):

            # Not stored yet - store it
            if string_representation not in self.stored_computations:
                self.stored_computations[string_representation] = result

            # Stored already but with a different value - something fishy is going on...
            elif self.stored_computations[string_representation] != result:
                io.write("Uh-oh:", string_representation, "has already been cached, but with a different value...", console_override=True)

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

    def probability(self, head: list, body: list, depth=0) -> float:
        """
        Compute the probability of some head given some body
        :param head: A list of some number of Outcome objects
        :param body: A list of some number of Outcome objects
        :param depth: Used for horizontal offsets in outputting info
        :return: A probability between [0.0, 1.0]
        """
        ###############################################
        #   Begin with bookkeeping / error-checking   #
        ###############################################

        # Sort the head and body if enabled
        if access("topological_sort_variables"):
            head, body = self.descendant_first_variable_sort(head), self.descendant_first_variable_sort(body)

        # Create a string representation of this query, and see if it's been done / in-progress / contradictory
        str_rep = self.p_str(head, body)

        # Print the actual query being made on each recursive call to help follow
        io.write("Querying:", str_rep, x_offset=depth)

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

        ###############################################
        #             Reverse product rule            #
        #   P(y, x | ~z) = P(y | x, ~z) * P(x | ~z)   #
        ###############################################

        if len(head) > 1:
            try:
                io.write("Applying reverse product rule to", str_rep)

                result_1 = self.probability(head[:-1], [head[-1]] + body, depth+1)
                result_2 = self.probability([head[-1]], body, depth+1)
                result = result_1 * result_2

                io.write(str_rep, "=", str(result), x_offset=depth)
                self.store_computation(str_rep, result)
                return result
            except ProbabilityException:
                io.write("Failed to resolve by reverse product rule.", x_offset=depth)

        ###############################################
        #            Attempt direct lookup            #
        ###############################################

        if len(head) == 1 and set(self.tables[head[0].name].given) == set(v.name for v in body):

            io.write("Querying table for: ", self.p_str(head, body), x_offset=depth, end="")
            table = self.tables[head[0].name]                       # Get table
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

                result_1 = self.probability(child, head + new_body, depth+1)
                result_2 = self.probability(head, new_body, depth+1)
                result_3 = self.probability(child, new_body, depth+1)
                if result_3 == 0:       # Avoid dividing by 0!
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

                        result_1 = self.probability(head, [as_outcome] + body, depth+1)
                        result_2 = self.probability([as_outcome], body, depth+1)
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

            head_variable = self.variables[head[0].name]
            can_drop = [v for v in body if v.name not in self.graph.parents(head_variable)]

            if can_drop:
                try:
                    io.write("Can drop:", str([str(item) for item in can_drop]), x_offset=depth)
                    result = self.probability(head, list(set(body) - set(can_drop)), depth+1)
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
        maximum_depth = max(self.graph.get_topology(v) for v in self.variables) + 1
        io.write("*** Topological Sort ***", end="", console_override=True)
        for depth in range(maximum_depth):
            this_depth = [self.variables[item].name for item in self.variables if self.variables[item].topological_order == depth]
            io.write("Depth", str(depth) + ":", ", ".join(sorted(this_depth)), end="", console_override=True)
        io.write(console_override=True)

    def missing_parents(self, variable: CG_Types, parent_subset: set) -> list:
        """
        Get a list of all the missing parents of a variable
        :param variable: A variable object (either string or the object itself) or an Outcome
        :param parent_subset: A set of parent strings
        :return: The remaining parents of the given variable, as a list
        """
        return list(self.graph.parents(variable) - parent_subset)

    def topological_variable_sort(self, variables: list) -> list:
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

    def descendant_first_variable_sort(self, variables: list) -> list:
        """
        A helper function to "sort" a list of Variables/Outcomes/Interventions such that no element has a
        "parent"/"ancestor" to its left
        :param variables: A list of any number of Variable/Outcome/Intervention instances
        :return: A sorted list, such that any instance has no ancestor earlier in the list
        """
        # We can already do top-down sorting, just reverse the answer
        return self.topological_variable_sort(variables)[::-1]

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

