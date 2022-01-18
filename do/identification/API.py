from itertools import product
from typing import Mapping, Set, Tuple, Union

from ..core.Model import Model
from ..core.Variables import Intervention, Outcome

from .LatentGraph import latent_transform
from .Identification import Identification
from .PExpression import PExpression, TemplateExpression


class API:

    def identification(self, y: Set[Outcome], x: Set[Intervention], model: Model, include_proof: bool = False) -> Union[float, Tuple[float, str]]:
        
        endogenous = set(model._v.keys())
        exogenous = model._g.v - endogenous

        latent = latent_transform(model._g.copy(), exogenous)
        
        p = PExpression([], [TemplateExpression(x, list(latent.parents(x))) for x in latent.v])
        expression = Identification({v.name for v in y}, {v.name for v in x}, p, latent, True)

        def _process(current: Union[PExpression, TemplateExpression], known: Mapping[str, str]):
            
            if isinstance(current, TemplateExpression):
                t = model.table(current.head)
                return t.probability_lookup(Outcome(current.head, known[current.head]), [Outcome(v, known[v]) for v in model.variable(current.head).parents])

            elif len(current.sigma) == 0:
                i = 1
                for term in current.terms:
                    i *= _process(term, known)
                return i

            else:
                t = 0
                for values in product(*[model.variable(v).outcomes for v in current.sigma]):
                    i = 1
                    for term in current.terms:
                        i *= _process(term, known | dict(zip(current.sigma, values)))
                    t += i
                return t

        result = _process(expression, {v.name: v.outcome for v in y} | {v.name: v.outcome for v in x})

        return (result, expression.proof()) if include_proof else result

    def proof(self, y: Set[Outcome], x: Set[Intervention], model: Model) -> str:

        endogenous = set(model._v.keys())
        exogenous = model._g.v - endogenous

        latent = latent_transform(model._g.copy(), exogenous)
        
        p = PExpression([], [TemplateExpression(x, list(latent.parents(x))) for x in latent.v])
        expression = Identification({v.name for v in y}, {v.name for v in x}, p, latent, True)
        return expression.proof()
