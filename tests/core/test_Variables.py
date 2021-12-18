from do.core.Variables import Outcome, Intervention


o1 = Outcome("X", "x")
o2 = Outcome("X", "~x")
o3 = Outcome("Y", "y")

t1 = Intervention("X", "x")
t2 = Intervention("X", "~x")
t3 = Intervention("Y", "y")


def test_OutcomesInterventions():

    assert o1 == "X"
    assert o1 != o2 and o2 != o3

    o1_copy = o1.copy()

    assert o1 == o1_copy and o1 is not o1_copy

    assert t1 == "X"
    assert t1 != t2 and t2 != t3

    t1_copy = t1.copy()

    assert t1 == t1_copy and t1 is not t1_copy
    assert o1 != t1



def test_OutcomesInterventions():

    o1 = Outcome("X", "x")
    o2 = Outcome("X", "~x")
    o3 = Outcome("Y", "y")

    assert o1 == "X"
    assert o1 != o2 and o2 != o3

    o1_copy = o1.copy()

    assert o1 == o1_copy and o1 is not o1_copy

    t1 = Intervention("X", "x")
    t2 = Intervention("X", "~x")
    t3 = Intervention("Y", "y")

    assert t1 == "X"
    assert t1 != t2 and t2 != t3

    t1_copy = t1.copy()

    assert t1 == t1_copy and t1 is not t1_copy
    assert o1 != t1




def test_OutcomesInterventions():

    o1 = Outcome("X", "x")
    o2 = Outcome("X", "~x")
    o3 = Outcome("Y", "y")

    assert o1 == "X"
    assert o1 != o2 and o2 != o3

    o1_copy = o1.copy()

    assert o1 == o1_copy and o1 is not o1_copy

    t1 = Intervention("X", "x")
    t2 = Intervention("X", "~x")
    t3 = Intervention("Y", "y")

    assert t1 == "X"
    assert t1 != t2 and t2 != t3

    t1_copy = t1.copy()

    assert t1 == t1_copy and t1 is not t1_copy
    assert o1 != t1




def test_OutcomesInterventions():

    o1 = Outcome("X", "x")
    o2 = Outcome("X", "~x")
    o3 = Outcome("Y", "y")

    assert o1 == "X"
    assert o1 != o2 and o2 != o3

    o1_copy = o1.copy()

    assert o1 == o1_copy and o1 is not o1_copy

    t1 = Intervention("X", "x")
    t2 = Intervention("X", "~x")
    t3 = Intervention("Y", "y")

    assert t1 == "X"
    assert t1 != t2 and t2 != t3

    t1_copy = t1.copy()

    assert t1 == t1_copy and t1 is not t1_copy
    assert o1 != t1




def test_OutcomesInterventions():

    o1 = Outcome("X", "x")
    o2 = Outcome("X", "~x")
    o3 = Outcome("Y", "y")

    assert o1 == "X"
    assert o1 != o2 and o2 != o3

    o1_copy = o1.copy()

    assert o1 == o1_copy and o1 is not o1_copy

    t1 = Intervention("X", "x")
    t2 = Intervention("X", "~x")
    t3 = Intervention("Y", "y")

    assert t1 == "X"
    assert t1 != t2 and t2 != t3

    t1_copy = t1.copy()

    assert t1 == t1_copy and t1 is not t1_copy
    assert o1 != t1
