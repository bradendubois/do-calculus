from pathlib import Path

from do.API import API

from do.core.Exceptions import MissingVariable
from do.core.Expression import Expression
from do.core.Inference import inference
from do.core.Model import from_yaml
from do.core.Variables import Outcome

api = API()

file_s = "tests/graphs/quick.yml"
file_p = Path(file_s)

m = from_yaml(file_s)


def test_Latent():
    q = Expression([Outcome("Y", "y")], [Outcome("X", "x")])
    assert(api.probability(q, m)) == 0.3

def test_Latent_bayes():
    q = Expression([Outcome("X", "x")], [Outcome("Y", "y")])
    print(api.probability(q, m))
