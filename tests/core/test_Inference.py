from os.path import dirname, abspath
from pathlib import Path
from yaml import safe_load

from do.API import API
from do.core.Model import from_dict
from do.core.Expression import Expression
from do.core.Variables import parse_outcomes_and_interventions

from do.core.helpers import within_precision

from ..source import api, models

test_file_directory = Path(dirname(abspath(__file__))) / "inference_files"


def test_Inference():

    files = sorted(list(filter(lambda x: x.suffix.lower() == ".yml", test_file_directory.iterdir())))
    assert len(files) > 0, "Inference test files not found"

    for file in files:

        with file.open("r") as f:
            data = safe_load(f)
        
        m = models[data["graph_filename"]]

        for test in data["tests"]:

            head = parse_outcomes_and_interventions(test["head"])
            body = parse_outcomes_and_interventions(test["body"]) if "body" in test else set()

            expected = test["expect"]

            result = api.probability(Expression(head, body), m)
            assert within_precision(result, expected)
