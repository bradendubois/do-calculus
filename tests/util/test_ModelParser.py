from pathlib import Path

from do.util.ModelLoader import parse_model

from ..test_driver import json_model, test_file


def test_parse_model():

    # nonexistent file
    try:
        parse_model(Path("fake", "path", "fake"))
        raise Exception     # coverage: skip
    except FileNotFoundError:
        pass

    # invalid file
    try:
        parse_model(Path("do", "util", "helpers.py"))
        raise Exception     # coverage: skip
    except FileNotFoundError:
        pass

    # string path
    parse_model(str(test_file.absolute()))

    # yml
    parse_model(test_file)

    # json
    parse_model(json_model)

    # latent variable
    parse_model(Path("do", "graphs", "test.json"))
