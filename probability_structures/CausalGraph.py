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

from probability_structures.BackdoorController import BackdoorController
from probability_structures.ConditionalProbabilityTable import ConditionalProbabilityTable
from probability_structures.Graph import *
from probability_structures.Probability_Engine import ProbabilityEngine
from probability_structures.VariableStructures import *

from utilities.IO_Logger import *
from utilities.parsing.UserIndexSelection import *
from utilities.parsing.ProbabilityString import *
from utilities.ResultCache import *

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

    def __init__(self, graph: Graph, variables: dict, outcomes: dict, tables: dict, functions: dict, **kwargs):

        # Clear the cached computations, since a different Causal Graph may have defined and cached computations with
        #   the same Variable names
        stored_computations.clear()

        # Save all the initializer attributes given
        self.graph = graph          # This graph shouldn't be modified once given
        self.variables = variables  # Maps string name to the Variable object instantiated
        self.outcomes = outcomes    # Maps string name *and* corresponding variable to a list of outcome values
        self.tables = tables        # Maps to corresponding tables
        self.functions = functions  # Maps to the functions a variable may be resolved by

    # Probability Query

    def probability_query(self, head, body):
        """
        Compute a query P(Y | X), modifying the graph given as necessary to make it possible
        :param head: The head of our query, the Y in P(Y | X)
        :param body: The body of our query, the X in P(Y | X)
        :return: A value between [0.0, 1.0] of the resulting probability
        """

        # String representation of the given query
        str_rep = p_str(head, body)

        # Begin logging
        io.write("Query:", str_rep, console_override=io.console_enabled)
        io.open(str_rep)

        # If there is no Intervention related work, we can compute a pretty standard query and exit early
        if not any(isinstance(g, Intervention) for g in body):

            # Compute
            engine = ProbabilityEngine(self.graph, self.outcomes, self.tables)
            probability = engine.probability((head, body))

        # There are interventions; need to find some valid Z to compute
        else:

            # Create a Backdoor Controller
            backdoor_controller = BackdoorController(self.graph)

            # Then, we take set Z and take Sigma_Z P(Y | do(X)) * P(Z)
            x = set([x.name for x in head])
            y = set([y.name for y in body if isinstance(y, Intervention)])
            deconfounding_sets = backdoor_controller.get_all_z_subsets(y, x)

            # Filter out our Z sets with observations in them and verify there are still sets Z
            deconfounding_sets = [s for s in deconfounding_sets if not any(g.name in s for g in body if not isinstance(g, Intervention))]
            if len(deconfounding_sets) == 0:
                io.write("No deconfounding set Z can exist for the given data.", console_override=True)
                return

            # Disable the incoming edges into our do's, and compute
            self.graph.disable_incoming(*[var for var in body if isinstance(var, Intervention)])
            probability = self.probability_query_with_interventions(head, body, deconfounding_sets)
            self.graph.reset_disabled()

        # End logging and return
        result = str_rep+" = {0:.{precision}f}".format(probability, precision=access("output_levels_of_precision")+1)
        io.write(result, console_override=io.console_enabled)
        io.close()
        return probability

    def probability_query_with_interventions(self, outcome: list, given: list, deconfounding_sets: list) -> float:
        """
        Our "given" includes an Intervention/do(X); choose Z set(s) and return the probability of this do-calculus
        :param outcome: A list of Outcomes
        :param given: A list of Outcomes and/or Interventions
        :param deconfounding_sets: A list of sets, each a sufficient Z
        :return: A probability between 0 and 1 representing the probability of the query given some chosen Z set(s)
        """

        # Create our engine with a modified graph
        graph = self.graph.copy()
        graph.disable_incoming(*[i for i in given if isinstance(i, Intervention)])
        engine = ProbabilityEngine(graph, self.outcomes, self.tables)

        def single_z_set_run(given_set) -> float:
            """
            Compute a probability from the given x and y, with the given z as a deconfounder
            :param given_set: A specific set Z
            :return: A probability P, between 0.0 and 1.0
            """
            p = 0.0     # Start at 0

            # We take every possible combination of outcomes of Z and compute each probability separately
            for cross in itertools.product(*[self.outcomes[var] for var in given_set]):

                # Construct the respective Outcome list of each Z outcome cross product
                # z_outcomes = []
                # for cross_idx in range(len(given_set)):
                #    z_outcomes.append(Outcome(list(given_set)[cross_idx], cross[cross_idx]))
                z_outcomes = [Outcome(x, cross[i]) for i, x in enumerate(given_set)]

                # First, we do our P(Y | do(X), Z)
                io.write("Computing sub-query: ", p_str(outcome, given + z_outcomes))
                p_y_x_z = engine.probability((outcome, given + z_outcomes))
                # print(p_str(outcome, given + z_outcomes), "=", p_y_x_z)

                # Second, we do our P(Z)
                io.write("Computing sub-query: ", p_str(z_outcomes, given))
                p_z = engine.probability((z_outcomes, []))
                # print(p_str(z_outcomes, []), "=", p_z)

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
            io.write(str(z_set), "=", str(result), end="", console_override=True)

            if only_result is None:  # Storing first result
                only_result = result

            # If results do NOT match; error
            error_msg = "Error: Two distinct results from different Z sets: " + str(only_result) + "vs" + str(result)
            assert abs(result - only_result) < 0.00000001, error_msg
        return only_result

    # Probabilistic Function Resolve

    def probability_function_query(self, function: str, noise_function="", apply_noise=True, depth=0) -> (float, float):
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
        if str_rep in stored_computations:
            io.write(str_rep, "already computed.", x_offset=depth)
            return stored_computations[str_rep]

        # Evaluate each var(foo) value, getting a min and max, and store these; when we evaluate this function, we will
        # take every possible cross product across the set of all resolved var(foo) values, ultimately returning the
        # min and max
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
                result = self.probability_function_query(*function_data,
                                                         apply_noise=access("recursive_noise_propagation"),
                                                         depth=depth+1)

                # Store the (min, max) result, cache if desired
                nested_min_maxes.append(result)
                store_computation(" +- ".join(*function_data), result)

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
                result = ProbabilityEngine(self.graph, self.outcomes, self.tables).probability((head, body))
                io.write(p_str(head, body), "=", str(result), x_offset=depth)
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
                noise_range = self.probability_function_query(noise_function, "",
                                                              apply_noise=access("recursive_noise_propagation"),
                                                              depth=depth+1)
                noise = sum(noise_range) / 2
            all_results.extend((result - noise, result + noise))

        result = min(all_results), max(all_results)
        io.write(function, "evaluates to", str(result), x_offset=depth)
        store_computation(str_rep, result)

        return result

    # Joint Distribution Table

    def joint_distribution_table(self):
        """
        Generate and present a joint distribution table for the loaded graph.
        """
        # Sort the variables for some nice presentation
        sort_keys = sorted(self.variables.keys())

        # Get all the possible outcomes for each respective variable, stored as a list of lists, ordered mirroring keys
        sorted_outcomes = [self.variables[key].outcomes for key in sort_keys]
        results = []

        # Cross product of this list and calculate each probability
        for cross in itertools.product(*sorted_outcomes):

            # Construct each Outcome by pairing the sorted keys with the outcome chosen
            outcomes = [Outcome(sort_keys[i], cross[i]) for i in range(len(sort_keys))]
            result = self.probability_query(outcomes, [])
            results.append([",".join(cross), [], result])

        results.append(["Total:", [], sum(r[2] for r in results)])

        # Create the table, then print it (with some aesthetic offsetting)
        cpt = ConditionalProbabilityTable(Variable(",".join(sort_keys), [], []), [], results)
        io.write("Joint Distribution Table for: " + ",".join(sort_keys), "\n", str(cpt), console_override=True)

    # Topological Sort

    def topological_sort(self):
        """
        Generate and present a topological sorting of the graph
        """
        maximum_depth = max(self.graph.get_topology(v) for v in self.variables) + 1
        sorted_by_depth = self.graph.topological_variable_sort(list(self.variables.keys()))
        io.write("*** Topological Sort ***", end="", console_override=True)
        for depth in range(maximum_depth):
            this_depth = []
            while len(sorted_by_depth) > 0 and self.graph.get_topology(sorted_by_depth[0]) == depth:
                this_depth.append(sorted_by_depth.pop(0))
            io.write("Depth", str(depth) + ":", ", ".join(sorted(this_depth)), end="", console_override=True)
        io.write(console_override=True)
