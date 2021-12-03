from .ConditionalProbabilityTable import ConditionalProbabilityTable
from .Expression import Expression
from .Model import Model


class API:

    def validate(self, model: Model) -> bool:
        ...

    def probability(query: Expression, model: Model) -> float:
        ...

    def joint_distribution(self, model: Model) -> ConditionalProbabilityTable:

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
