from math import prod

from do.api.joint_distribution_table import api_joint_distribution_table
from do.structures.ConditionalProbabilityTable import ConditionalProbabilityTable
from do.util.helpers import within_precision

from ..test_driver import cg


def test_api_joint_distribution_table():

    jdt: ConditionalProbabilityTable = api_joint_distribution_table(cg)

    outcome_counts = list(map(lambda v: len(cg.outcomes[v]), cg.variables))
    totals = map(lambda row: row[-1], jdt.table_rows[:-1])

    assert isinstance(jdt, ConditionalProbabilityTable)
    assert len(jdt.table_rows[:-1]) == prod(outcome_counts)
    assert within_precision(sum(list(totals)), 1)
