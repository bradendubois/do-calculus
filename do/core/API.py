from .ConditionalProbabilityTable import ConditionalProbabilityTable
from .Expression import Expression
from .Inference import inference
from .Model import Model


class API:

    def validate(self, model: Model) -> bool:
        ...

    def probability(query: Expression, model: Model) -> float:
        return inference(query, model)
