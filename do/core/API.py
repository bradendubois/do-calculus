from .Types import Model

class API:

    def bar(self):
        print("bar")

    # Verify a model as valid
    def validate(self, model: Model):
        ...

    ...





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


def api_deconfounding_sets(bc: BackdoorController, src: Vertices, dst: Vertices) -> Collection[Collection[str]]:
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


def api_probability_query_parse(query: str) -> Dict[str, Collection[str]]:
    """
    Parse a query string into Outcome and Intervention structures.
    @param query: A string of the form "Y=y, X=x | W=w", or just "Y=y, X=x"
    @return A dictionary mapping "head" and "body" to lists of Outcome and Intervention objects
    """
    if "|" in query:
        l, r = query.split("|")
        return {
            "y": parse_outcomes_and_interventions(l),
            "x": parse_outcomes_and_interventions(r)
        }

    return {
        "y": parse_outcomes_and_interventions(query),
        "x": set()
    }


def api_probability_query(cg: CausalGraph, y: Collection[Outcome], x: Collection[Union[Outcome, Intervention]]) -> float:
    """
    Compute a probability query for the currently loaded causal graph.
    @param cg: A Causal Graph containing variables, distributions, etc.
    @param y: A set of Outcome objects that exist in the given Causal Graph
    @param x: A set of Outcome and/or Intervention objects that exist in the given Causal Graph
    @return A value in the range [0.0, 1.0] corresponding to the given probability
    @raise ProbabilityException when the given probability can not be computed, due to an undefined variable, etc.
    """
    return cg.probability_query(y, x)
