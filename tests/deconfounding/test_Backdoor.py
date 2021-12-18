from os.path import dirname, abspath
from pathlib import Path
from typing import Collection, Mapping
from yaml import safe_load as load

from do.API import API
from do.core.Expression import Expression
from do.core.Model import Model, from_dict
from do.core.Variables import Intervention, parse_outcomes_and_interventions
from do.core.helpers import within_precision

test_file_directory = Path(dirname(abspath(__file__))) / "test_files"


def deconfounding_validation(model: Model, tests: Collection[Mapping]):

    api = API()

    for test in tests:

        expect = test["expect"]
        v = test["type"]

        if v == "backdoors":
            src = test["src"]
            dst = test["dst"]
            dcf = test["dcf"] if "dcf" in test else []
            result = api.backdoors(src, dst, model.graph(), dcf)
            assert all(x in expect for x in result)
            if test["exhaustive"]:
                assert len(result) == len(expect)

        elif v == "treatment":
            head = parse_outcomes_and_interventions(test["head"])
            body = parse_outcomes_and_interventions(test["body"])

            o = list(filter(lambda x: not isinstance(x, Intervention), body))
            i = list(filter(lambda x: isinstance(x, Intervention), body))

            assert within_precision(api.treat(Expression(head, o), i, model), expect)

        else:
            raise Exception("unexpected test type")


def test_Deconfounding():

    files = sorted(list(filter(lambda x: x.suffix.lower() == ".yml", test_file_directory.iterdir())))
    assert len(files) > 0, f"Found no backdoor module tests"

    for test_file in files:

        with test_file.open("r") as f:
            yml_test_data = load(f)

        graph_filename = yml_test_data["graph_filename"]        
        with (test_file_directory / "graphs" / graph_filename).open("r") as f:
            graph_data = load(f)

        model = from_dict(graph_data)
        deconfounding_validation(model, yml_test_data["tests"])
