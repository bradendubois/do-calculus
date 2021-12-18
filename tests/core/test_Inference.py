from os.path import dirname, abspath
from pathlib import Path
from yaml import safe_load as load

from do.API import API
from do.core.Model import from_dict
from do.core.Expression import Expression
from do.core.Variables import parse_outcomes_and_interventions

from do.core.helpers import within_precision

test_file_directory = Path(dirname(abspath(__file__))) / "test_files"


def test_Inference():

    api = API()

    files = sorted(list(filter(lambda x: x.suffix.lower() == ".yml", test_file_directory.iterdir())))
    assert len(files) > 0, "Inference test files not found"

    for model in files:

        with model.open("r") as f:
            yml_model = load(f)

        g = yml_model["graph_filename"]
        with (test_file_directory / "graphs" / g).open("r") as f:
            g_data = load(f)
        
        m = from_dict(g_data)

        for test in yml_model["tests"]:

            head = parse_outcomes_and_interventions(test["head"])
            body = parse_outcomes_and_interventions(test["body"]) if "body" in test else set()

            expected = test["expect"]

            result = api.probability(Expression(head, body), m)
            assert within_precision(result, expected)
