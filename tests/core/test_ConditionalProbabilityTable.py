from pytest import raises

from do.API import API
from do.core.Exceptions import MissingTableRow
from do.core.Variables import Outcome

from ..source import models

model = models["pearl-3.4.yml"]
table = model.table("Xj")
priors = [Outcome("X6", "x6"), Outcome("X4", "x4"), Outcome("X5", "x5")]

api = API()


def test_ValidLookup():
    table.probability_lookup(Outcome("Xj", "xj"), priors)


def test_InvalidLookup():
    with raises(MissingTableRow):
        table.probability_lookup(Outcome("Xj", "foo"), priors)
