from pathlib import Path
from typing import Union

from .Expression import Expression
from .Inference import inference, validate
from .Model import Model, from_dict, from_path


class API:

    def validate(self, model: Model) -> bool:
        return validate(model)

    def probability(self, query: Expression, model: Model) -> float:
        return inference(query, model)

    def instantiate_model(self, model_target: Union[str, Path, dict]) -> Model:
        
        if isinstance(model_target, dict):
            return from_dict(model_target)

        return from_path(Path(model_target) if isinstance(model_target, str) else model_target)
