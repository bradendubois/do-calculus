from .Expression import Expression
from .Inference import inference, validate
from .Model import Model


class API:

    def validate(self, model: Model) -> bool:
        return validate(model)

    def probability(self, query: Expression, model: Model) -> float:
        return inference(query, model)
