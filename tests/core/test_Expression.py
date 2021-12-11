from pytest import raises

from do.core.Exceptions import EmptyExpressionHead
from do.core.Expression import Expression
from do.core.Variables import Outcome


def test_SequenceSequence():
    x = Expression([Outcome("Y", "y"), Outcome("X", "x")], [Outcome("Z", "z")])
    assert str(x) == "P(Y = y, X = x | Z = z)" or str(x) == "P(X = x, Y = y | Z = z)"

def test_SequenceSet():
    x = Expression([Outcome("Y", "y"), Outcome("X", "x")], {Outcome("Z", "z")})
    assert str(x) == "P(Y = y, X = x | Z = z)" or str(x) == "P(X = x, Y = y | Z = z)"

def test_SequenceSingle():
    x = Expression([Outcome("Y", "y"), Outcome("X", "x")], Outcome("Z", "z"))
    assert str(x) == "P(Y = y, X = x | Z = z)" or str(x) == "P(X = x, Y = y | Z = z)"

def test_SequenceNone():
    x = Expression([Outcome("Y", "y"), Outcome("X", "x")])
    assert str(x) == "P(Y = y, X = x)" or str(x) == "P(X = x, Y = y)"


def test_SetSequence():
    x = Expression({Outcome("Y", "y"), Outcome("X", "x")}, [Outcome("Z", "z")])
    print(str(x))
    assert str(x) == "P(Y = y, X = x | Z = z)" or str(x) == "P(X = x, Y = y | Z = z)"

def test_SetSet():
    x = Expression({Outcome("Y", "y"), Outcome("X", "x")}, {Outcome("Z", "z")})
    print(str(x))
    assert str(x) == "P(Y = y, X = x | Z = z)" or str(x) == "P(X = x, Y = y | Z = z)"

def test_SetSingle():
    x = Expression({Outcome("Y", "y"), Outcome("X", "x")}, Outcome("Z", "z"))
    assert str(x) == "P(Y = y, X = x | Z = z)" or str(x) == "P(X = x, Y = y | Z = z)"

def test_SetNone():
    x = Expression({Outcome("Y", "y"), Outcome("X", "x")})
    assert str(x) == "P(Y = y, X = x)" or str(x) == "P(X = x, Y = y)"


def test_SingleSequence():
    x = Expression(Outcome("Y", "y"), [Outcome("Z", "z")])
    assert str(x) == "P(Y = y | Z = z)"

def test_SingleSet():
    x = Expression(Outcome("Y", "y"), {Outcome("Z", "z")})
    assert str(x) == "P(Y = y | Z = z)"

def test_SingleSingle():
    x = Expression(Outcome("Y", "y"), Outcome("Z", "z"))
    assert str(x) == "P(Y = y | Z = z)"

def test_SingleNone():
    x = Expression(Outcome("Y", "y"))
    assert str(x) == "P(Y = y)"


def test_NoneSequence():
    with raises(EmptyExpressionHead):    
        Expression(None, [Outcome("Z", "z")])

def test_NoneNone():
    with raises(EmptyExpressionHead):    
        Expression(None)
