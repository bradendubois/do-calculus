from do.core.Variables import Outcome, Intervention


o1 = Outcome("X", "x")
o2 = Outcome("X", "~x")
o3 = Outcome("Y", "y")

t1 = Intervention("X", "x")
t2 = Intervention("X", "~x")
t3 = Intervention("Y", "y")


def test_Outcome():
    assert o1 == "X"
    assert o2 == "X"
    assert o3 == "Y"


def test_Intervention():
    assert t1 == "X"
    assert t2 == "X"
    assert t3 == "Y"


def test_OutcomesEquality():
    assert o1.name == o2.name and o1 != o2
    assert o2 != o3
    assert o1 != o3
    o1_copy = o1.copy()
    assert o1 == o1_copy
    assert o1 is not o1_copy


def test_InterventionEquality():
    assert t1.name == t2.name and t1 != t2
    assert t2 != t3
    assert t1 != t3
    t1_copy = t1.copy()
    assert t1 == t1_copy
    assert t1 is not t1_copy


def test_OutcomesInterventionEquality():
    assert o1.name == t1.name and o1 != t1
    assert o2.name == t2.name and o2 != t2
    assert o3.name == t3.name and o3 != t3
