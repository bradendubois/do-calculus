#########################################################
#                                                       #
#   Causal Graph                                        #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

from itertools import product
from typing import Collection, Union

from .BackdoorController import BackdoorController
from .Graph import Graph
from .Probability_Engine import ProbabilityEngine
from .VariableStructures import Outcome, Intervention

from ..config.settings import Settings
from ..util.OutputLogger import OutputLogger
from ..util.helpers import p_str


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

    def probability_query(self, head: Collection[Outcome], body: Collection[Union[Outcome, Intervention]]) -> float:
        """
        Compute a probability in the given model.
        @param head: A set of Outcome objects
        @param body: A set of Outcome and/or Intervention objects.
        @return: A value in the range [0.0, 1.0] if the probability can be computed, None otherwise.
        """
        def strings(s: Collection[Union[Outcome, Intervention]]):
            return set(map(lambda x: x.name, s))

        head = set(head)
        body = set(body)

        self.graph.reset_disabled()

        # String representation of the given query
        str_rep = p_str(list(head), list(body))
        self.output.detail(f"Query: {str_rep}")

        interventions = set(filter(lambda x: isinstance(x, Intervention), body))
        observations = body - interventions

        # If there are no Interventions, we can compute a standard query
        if len(interventions) == 0:

            engine = ProbabilityEngine(self.graph, self.outcomes, self.tables)
            probability = engine.probability(head, body)

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
                probability = engine.probability(head, body)

            # Backdoor paths found; find deconfounding set to compute
            else:

                # Find all possible deconfounding sets, and use possible subsets
                deconfounding_sets = bc.all_dcf_sets(src, dst)

                # Filter down the deconfounding sets not overlapping with our query body
                vertex_dcf = list(filter(lambda s: len(set(s) & strings(body)) == 0, deconfounding_sets))
                assert len(vertex_dcf) != 0, "No deconfounding set Z can exist for the given data."

                # Compute with every possible deconfounding set as a safety measure; ensuring they all match
                probability = None  # Sentinel value
                for z_set in vertex_dcf:

                    result = self._marginalize_query(head, body, z_set)
                    if probability is None:  # Storing first result
                        probability = result

                    # If results do NOT match; error
                    assert abs(result-probability) < 0.00000001,  f"Error: Distinct results: {probability} vs {result}"

        msg = "{0} = {1:.{precision}f}".format(str_rep, probability, precision=Settings.output_levels_of_precision + 1)
        self.output.detail(msg)
        self.graph.reset_disabled()
        return probability

    def _marginalize_query(self, head: Collection[Outcome], body: Collection[Union[Outcome, Intervention]], dcf: Collection[str]) -> float:
        """
        Handle the modified query where we require a deconfounding set due to Interventions / treatments.
        @param head: The head of the query, a set containing Outcome objects
        @param body: The body of the query, a set containing Outcome and Intervention objects
        @param dcf: A set of (string) names of variables to serve as a deconfounding set, blocking all backdoor paths
            between the head and body
        @return:
        """

        head = set(head)
        body = set(body)

        interventions = set(filter(lambda x: isinstance(x, Intervention), body))

        # Augment graph (isolating interventions as roots) and create engine
        self.graph.disable_incoming(*interventions)
        engine = ProbabilityEngine(self.graph, self.outcomes, self.tables)

        probability = 0.0

        # We take every possible combination of outcomes of Z and compute each probability separately
        for cross in product(*[self.outcomes[var] for var in dcf]):

            # Construct the respective Outcome list of each Z outcome cross product
            z_outcomes = {Outcome(x, cross[i]) for i, x in enumerate(dcf)}

            # First, we do P(Y | do(X), Z)
            self.output.detail(f"Computing sub-query: {p_str(list(head), list(body | z_outcomes))}")
            p_y_x_z = engine.probability(head, body | set(z_outcomes))

            # Second, P(Z)
            self.output.detail(f"Computing sub-query: {p_str(list(z_outcomes), list(body))}")
            p_z = engine.probability(z_outcomes, body)

            probability += p_y_x_z * p_z

        return probability
