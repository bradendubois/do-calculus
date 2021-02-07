#########################################################
#                                                       #
#   Causal Graph                                        #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

from itertools import product

from src.probability.structures.BackdoorController import BackdoorController
from src.probability.structures.ConditionalProbabilityTable import ConditionalProbabilityTable
from src.probability.structures.Graph import *
from src.probability.structures.Probability_Engine import ProbabilityEngine
from src.probability.structures.VariableStructures import *

from src.util.Output_Logger import OutputLogger
from src.util.parsers.ProbabilityString import *
from src.util.ResultCache import *

# Union all Variable types with string for functions that can take any of these
CG_Types = str or Variable or Outcome or Intervention


class CausalGraph:
    """Handles probability queries / joint distributions on the given Causal Graph"""

    def __init__(self, graph: Graph, variables: dict, outcomes: dict, tables: dict, latent: set, **kwargs):
        """
        Initialize a Causal Graph to compute standard probability queries as well as interventional, as per the
        do-calculus of Judea Pearl, with deconfounding sets handled automatically.
        @param graph: A Graph object representing a given model
        @param variables: A dictionary mapping a string name of a variable to a Variable object
        @param outcomes: A dictionary mapping both a string name of a Variable, as well as the Variable object itself
            to a list of possible outcome values for the variable.
        @param tables: A dictionary mapping both a string name of a Variable, as well as the Variable object itself to
            a given ConditionalProbabilityTable object.
        @param latent: A set of variables, both string name as well as the Variable object itself, representing all
            latent (unobservable) variables in the given model.
        @param kwargs: Any arbitrary additional keyword arguments, allowing a model loaded using a library to be
            unpacked into an initializer call using the ** prefix.
        """
        self.graph = graph.copy()
        self.variables = variables.copy()
        self.outcomes = outcomes.copy()
        self.tables = tables.copy()
        self.latent = latent.copy()
        self.output = kwargs["output"] if "output" in kwargs else OutputLogger()

    def probability_query(self, head: set, body: set) -> float or None:
        """
        Compute a probability in the given model.
        @param head: A set of Outcome objects
        @param body: A set of Outcome and/or Intervention objects.
        @return: A value in the range [0.0, 1.0] if the probability can be computed, None otherwise.
        """
        def strings(s: set):
            return set(map(lambda x: x.name, s))

        self.graph.reset_disabled()

        # String representation of the given query
        str_rep = p_str(list(head), list(body))
        self.output.detail(f"Query: {str_rep}")

        interventions = set(filter(lambda x: isinstance(x, Intervention), body))
        observations = body - interventions

        # If there are no Interventions, we can compute a standard query
        if len(interventions) == 0:

            engine = ProbabilityEngine(self.graph, self.outcomes, self.tables)
            probability = engine.probability((head, body))

        # There are interventions; may need to find some valid Z to compute
        else:

            bc = BackdoorController(self.graph)

            src = strings(interventions)
            dst = strings(head)
            dcf = strings(observations)

            # No backdoor paths; augment graph space and compute
            if len(bc.backdoor_paths(src, dst, dcf)) == 0:

                # Block all the incoming edges for interventions, making them roots
                self.graph.disable_incoming(*interventions)

                engine = ProbabilityEngine(self.graph, self.outcomes, self.tables)
                probability = engine.probability((head, body))

            # Backdoor paths found; find deconfounding set to compute
            else:

                # Find all possible deconfounding sets, and use possible subsets
                deconfounding_sets = bc.all_dcf_sets(src, dst)

                # Filter down the deconfounding sets not overlapping with our query body
                vertex_dcf = list(filter(lambda s: len(set(s) & strings(body)) == 0, deconfounding_sets))
                if len(vertex_dcf) == 0:
                    self.output.result("No deconfounding set Z can exist for the given data.")
                    return

                # Compute with every possible deconfounding set as a safety measure; ensuring they all match
                probability = None  # Sentinel value
                for z_set in vertex_dcf:

                    result = self._marginalize_query(head, body, interventions, z_set)
                    if probability is None:  # Storing first result
                        probability = result

                    # If results do NOT match; error
                    assert abs(result-probability) < 0.00000001,  f"Error: Distinct results: {probability} vs {result}"

        msg = "{} = {0:.{precision}f}".format(str_rep, probability, precision=access("output_levels_of_precision") + 1)
        self.output.result(msg)
        self.graph.reset_disabled()
        return probability

    def _marginalize_query(self, head: set, body: set, interventions: set, dcf: set) -> float:
        """
        Handle the modified query where we require a deconfounding set due to Interventions / treatments.
        @param head: The head of the query, a set containing Outcome objects
        @param body: The body of the query, a set containing Outcome and Intervention objects
        @param interventions: A set containing Intervention objects; this should be a subset within body, of all
            Intervention objects in the query, since this should already have been found whenever this function is
            called.
        @param dcf: A set of (string) names of variables to serve as a deconfounding set, blocking all backdoor paths
            between the head and body
        @return:
        """

        # Augment graph (isolating interventions as roots) and create engine
        self.graph.disable_incoming(*interventions)
        engine = ProbabilityEngine(self.graph, self.outcomes, self.tables)

        probability = 0.0

        # We take every possible combination of outcomes of Z and compute each probability separately
        for cross in product(*[self.outcomes[var] for var in dcf]):

            # Construct the respective Outcome list of each Z outcome cross product
            z_outcomes = [Outcome(x, cross[i]) for i, x in enumerate(dcf)]

            # First, we do P(Y | do(X), Z)
            self.output.detail(f"Computing sub-query: {p_str(list(head), list(body) + z_outcomes)}")
            p_y_x_z = engine.probability((head, body | set(z_outcomes)))

            # Second, P(Z)
            self.output.detail(f"Computing sub-query: {p_str(z_outcomes, list(body))}")
            p_z = engine.probability((z_outcomes, body))

            probability += p_y_x_z * p_z

        return probability

    # Joint Distribution Table
    # TODO -> Move these into API?

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
        for cross in product(*sorted_outcomes):

            # Construct each Outcome by pairing the sorted keys with the outcome chosen
            outcomes = [Outcome(sort_keys[i], cross[i]) for i in range(len(sort_keys))]
            result = self.probability_query(set(outcomes), set())
            results.append([",".join(cross), [], result])

        results.append(["Total:", [], sum(r[2] for r in results)])

        # Create the table, then print it (with some aesthetic offsetting)
        cpt = ConditionalProbabilityTable(Variable(",".join(sort_keys), [], []), [], results)
        self.output.result(f"Joint Distribution Table for: {','.join(sort_keys)}")
        self.output.result(f"{cpt}")

    # Topological Sort

    def topological_sort(self):
        """
        Generate and present a topological sorting of the graph
        """
        maximum_depth = max(self.graph.get_topology(v) for v in self.variables) + 1
        sorted_by_depth = self.graph.topological_variable_sort(list(self.variables.keys()))
        self.output.result("*** Topological Sort ***" + "\n")
        for depth in range(maximum_depth):
            this_depth = []
            while len(sorted_by_depth) > 0 and self.graph.get_topology(sorted_by_depth[0]) == depth:
                this_depth.append(sorted_by_depth.pop(0))
            self.output.result("Depth {}: {}".format(depth, ", ".join(sorted(this_depth))))
