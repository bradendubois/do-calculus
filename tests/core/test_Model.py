from pytest import raises

from do.core.Exceptions import MissingVariable

from ..source import models
model = models["pearl-3.4.yml"]


def test_Lookup():

    # these should raise no issue
    assert model.variable("Xj")
    assert model.variable("Xi")
    
    # ensure a latent variable fails to be retrieved...
    with raises(MissingVariable):
        model.variable("Z")
