from do.structures.ConditionalProbabilityTable import ConditionalProbabilityTable
from do.structures.Exceptions import MissingTableRow
from do.structures.VariableStructures import Outcome

from tests.test_driver import cg


def test_probability_lookup():
    t: ConditionalProbabilityTable = cg.tables["Xj"]

    priors = [Outcome("X6", "x6"), Outcome("X4", "x4"), Outcome("X5", "x5")]

    assert t.probability_lookup(Outcome("Xj", "xj"), priors) == 0.0
    assert t.probability_lookup(Outcome("Xj", "~xj"), priors) == 1.0

    try:
        t.probability_lookup(Outcome("Xj", "foo"), priors)
        raise Exception     # coverage: skip
    except MissingTableRow:
        pass
