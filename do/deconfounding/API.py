from itertools import product
from typing import Collection, Dict, Optional, Union

from ..core.ConditionalProbabilityTable import ConditionalProbabilityTable
from ..core.Expression import Expression
from ..core.Model import Model
from ..core.Types import Vertex, Path
from ..core.Variables import Intervention, Outcome, Variable, parse_outcomes_and_interventions

from .Backdoor import BackdoorController
from .CausalGraph import CausalGraph


class API:

    def api_joint_distribution_table(cg: CausalGraph) -> ConditionalProbabilityTable:
        """
        Compute and return a joint distribution table for the given model.
        @param cg: A CausalGraph to compute the JDT for.
        @return: A list of sets, where each item is a tuple, (Outcomes, P), where the first item is a set containing one
            Outcome object for each variable in the model, and the second is the respective probability.
        """
        sorted_keys = sorted(cg.variables.keys())
        results = []

        for cross in product(*list(map(lambda x: cg.outcomes[x], sorted_keys))):
            outcomes = {Outcome(x, cross[i]) for i, x in enumerate(sorted_keys)}
            results.append((outcomes, cg.probability_query(outcomes, set())))

        keys = sorted(cg.variables.keys())
        rows = [[",".join(map(str, outcomes)), [], p] for outcomes, p in results]
        rows.append(["Total:", [], sum(map(lambda r: r[1], results))])
        cpt = ConditionalProbabilityTable(Variable(",".join(keys), [], []), [], rows)

        return cpt

    def api_backdoor_paths_parse(query: str) -> Dict[str, Collection[str]]:
        """
        Convert a given query string into a pair of sets to compute all backdoor paths between
        @param query: A string of the form "X, Y, Z -> A, B, C" or "X, Y, Z -> A, B, C | I, J, K"
        @return A dictionary mapping "src", "dst", and "dcf" to sets, containing all vertices on the left and right sides
            of the arrow, and the third as all vertices are the right of the bar, respectively.
        """
        def clean(x):
            return set(map(lambda y: y.strip(), x.strip().split(",")))

        l, r = query.split("->")

        if "|" in r:
            s = r.split("|")
            r, dcf = clean(s[0]), clean(s[1])
        else:
            r, dcf = clean(r), set()

        return {
            "src": clean(l),
            "dst": r,
            "dcf": dcf
        }

    def api_backdoor_paths(bc: BackdoorController, src: Collection[Vertex], dst: Collection[Vertex], dcf: Optional[Collection[Vertex]]) -> Collection[Path]:
        """
        Compute and return all the backdoor paths from any vertex in src to any vertex in dst
        @param bc: A Backdoor Controller with a graph conforming to the given source and destination sets.
        @param src: A set of string vertices that are in the given Backdoor Controller, which will be the vertices to
            attempt to connect to vertices in dst by a backdoor path (s).
        @param dst: A set of string vertices that are in the given Backdoor Controller, which will be reached by vertices
            in src.
        @param dcf: A set of string vertices in the given Backdoor Controller, which will behave as a deconfounding set to
            block paths from src to dst.
        @return all backdoor paths connecting any vertex in src to a vertex in dst, by which each path is represented as a
            list containing each vertex (as a string) from the source vertex to the destination vertex, with dcf acting as
            a deconfounding set.
        """
        return bc.backdoor_paths(src, dst, dcf)



    def api_deconfounding_sets_parse(query: str) -> Dict[str, Collection[str]]:
        """
        Convert a given query string into a pair of sets to find all sufficient deconfounding sets between.
        @param query: A string of the form "X, Y, Z -> A, B, C"
        @return A dictionary of keys "src" and "dst" mapped to sets containing all vertices (as strings) on the left and
            right sides of the arrow, respectively.
        """
        def clean(x):
            return set(map(lambda y: y.strip(), x.strip().split(",")))

        src, dst = map(clean, query.split("->"))

        return {
            "src": src,
            "dst": dst
        }

    def api_deconfounding_sets(bc: BackdoorController, src: Collection[Vertex], dst: Collection[Vertex]) -> Collection[Collection[str]]:
        """
        Compute and return all the backdoor paths from any vertex in src to any vertex is dst
        @param bc: A Backdoor Controller with a graph conforming to the given source and destination sets.
        @param src: A set of string vertices that are in the given Backdoor Controller, which will be the vertices to
            attempt to connect to vertices in dst by a backdoor path (s).
        @param dst: A set of string vertices that are in the given Backdoor Controller, which will be reached by vertices
            in src.
        @return a list of sets, where each set - a set of string vertices - is sufficient at blocking all backdoor paths
            from any vertex in src to any other vertex in dst.
        """
        return bc.all_dcf_sets(src, dst)


    # TODO rework above api components

    def treat(self, expression: Expression, model: Model):
        ...
