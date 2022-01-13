from itertools import product
from typing import Mapping, Set, Union

from ..core.Expression import Expression
from ..core.Model import Model
from ..core.Variables import Intervention, Outcome

from .LatentGraph import LatentGraph
from .Identification import Identification
from .PExpression import PExpr, TemplateExpression


class API:

    def identification(self, y: Set[Outcome], x: Set[Intervention], model: Model):
        
        endogenous = set(model._v.keys())
        exogenous = model._g.v - endogenous

        latent = LatentGraph(model._g.copy(), exogenous)
        p = PExpr([], [[x, list(latent._g.parents(x))] for x in latent._g.v])
        expression = Identification(y, x, p, latent)

        def _process(current: Union[PExpr, TemplateExpression], known: Mapping[str, str]):
            
            if isinstance(current, TemplateExpression):
                
                t = model.table(current.head)
                return t.probability_lookup(Outcome(current.head), known[current.head], [Outcome(v, known[v]) for v in model.variable(current.head).parents])


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


        return _process(expression, {v.name: v.outcome for v in y} | {v.name: v.outcome for v in x})

    def proof(self, expression: Expression):
        ...

