from do.structures.VariableStructures import Variable, Outcome, Intervention

from ..test_driver import cg


# probability/structures/VariableStructures

def test_outcome():
    o1 = Outcome("X", "x")
    o2 = Outcome("X", "~x")
    o3 = Outcome("Y", "y")

    assert o1 != o2
    assert o1 == "X"
    assert o1 != o2 and o2 != o3

    o1_copy = o1.copy()

    assert o1 == o1_copy and o1 is not o1_copy


def test_variable():

    for v in cg.variables.values():

        v: Variable

        assert isinstance(v.name, str)
        assert isinstance(v.descendants, set)
        assert isinstance(v.parents, list)
        assert isinstance(v.topological_order, int)

        c = v.copy()

        assert v == c
        assert v is not c

        assert v.name == c.name

        assert v.descendants is not c.descendants
        assert v.descendants == c.descendants

        assert v.parents is not c.parents
        assert v.parents == c.parents

        assert v.topological_order == c.topological_order

        assert hash(v) == hash(c)

        # Unique enough hashing function
        assert list(map(lambda variable: hash(variable), cg.variables.values())).count(hash(v)) <= 3
        assert str(v) == str(c)

        assert v == v.name


def test_intervention():
    t1 = Intervention("X", "x")
    t2 = Intervention("X", "~x")
    t3 = Intervention("Y", "y")

    assert t1 != t2
    assert t1 == "X"
    assert t1 != t2 and t2 != t3

    t1_copy = t1.copy()

    assert t1 == t1_copy and t1 is not t1_copy


def test_parse_outcomes_and_interventions():
    ...

