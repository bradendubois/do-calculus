from do.util.helpers import disjoint, minimal_sets, power_set


def test_disjoint():
    d1 = {0, 1, 2, 3, 4}
    d2 = {3, 4, 5, 6, 7}
    d3 = {6, 7, 8, 9, 10}
    assert not disjoint(d1, d2)
    assert not disjoint(d2, d3)
    assert not disjoint(d1, d2, d3)
    assert disjoint(d1, d3)


def test_minimal_sets():
    s1 = {1, 2, 3}
    s2 = {1, 2, 3, 4}
    s3 = {0, 1, 2, 3, 4}
    s4 = {5, 6, 7}
    s5 = {0, 1, 2, 3, 4, 5, 6, 7}

    minimums = minimal_sets(s1, s2, s3, s4, s5)
    assert minimums == [s1, s4]

    assert minimal_sets(s1) == [s1]
    assert minimal_sets(s1, s2) == [s1]
    assert minimal_sets(s1, s4) == [s1, s4]


def test_power_set():
    data = [1, 2, 3, 4]
    with_empty = power_set(data, allow_empty_set=True)
    without_empty = power_set(data, allow_empty_set=False)
    assert len(set(with_empty)) == 2 ** len(data)
    assert len(set(without_empty)) == 2 ** len(data) - 1
