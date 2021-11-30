from typing import Collection, Dict

from .Expression import Expression
from .Model import Model

class API:

    def validate(self, model: Model):
        ...

    def probability(query: Expression, model: Model) -> float:
        ...
