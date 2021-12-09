from pathlib import Path
from do.core.Exceptions import MissingVariable
from do.core.Model import from_yaml

file_s = "tests/graphs/quick.yml"
file_p = Path(file_s)

def test_parse():

    m = from_yaml(file_s)
    
    # these should raise no issue
    assert m.variable("X")
    assert m.variable("Y")
    
    # ensure a latent variable fails to be retrieved...
    try:
        m.variable("Z")
        raise Exception
    except MissingVariable:
        pass
