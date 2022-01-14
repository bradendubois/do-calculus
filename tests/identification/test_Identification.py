from do.API import API
from do.core.Expression import Expression
from do.core.Variables import Intervention, Outcome
from do.core.helpers import within_precision

from ..source import models
melanoma = models["melanoma.yml"]
pearl34 = models["pearl-3.4.yml"]

api = API()

##################################################################################
"""
Some tests comparing the resulting value computed by ID as being the same as the
value computed by the standard inference and deconfounding modules. Some queries
don't require deconfounding, and ID should correctly handle these; some queries
require substantial deconfounding.
"""

def test_NoDeconfounding_Pearl34():
    assert within_precision(api.probability(Expression(Outcome("Xj", "xj")), pearl34), api.identification({Outcome("Xj", "xj")}, [], pearl34))


def test_NoDeconfounding_Melanoma():
    assert within_precision(api.probability(Expression(Outcome("Y", "y")), melanoma), api.identification({Outcome("Y", "y")}, [], melanoma))


def test_p34():
    assert within_precision(api.identification({Outcome("Xj", "xj")}, {Intervention("Xi", "xi")}, pearl34), api.treat(Expression(Outcome("Xj", "xj")), [Intervention("Xi", "xi")], pearl34))


def test_melanoma():
    assert within_precision(api.identification({Outcome("Y", "y")}, {Intervention("X", "x")}, melanoma), api.treat(Expression(Outcome("Y", "y")), [Intervention("X", "x")], melanoma))

def test_proof():
    print(api.proof({Outcome("Y", "y")}, {Intervention("X", "x")}, melanoma))

##################################################################################
