import itertools
from os.path import dirname, abspath
from pathlib import Path
from yaml import safe_load as load

from do.structures.BackdoorController import BackdoorController
from do.structures.Exceptions import IntersectingSets
from do.util.ModelLoader import parse_model

from tests.print_test_result import print_test_result

test_file_directory = Path(dirname(abspath(__file__))) / "test_files"


def model_backdoor_validation(bc: BackdoorController, test_data: dict) -> (bool, str):
    """
    Validate backdoor path tests provided against a given model
    @param bc: A BackdoorController containing the data necessary to compute
    @param test_data: a dictionary { "graph_filename": string, tests: [] } where each test in the list is of the form
        { "src": [], "dst": [], "expect": [[], [], []], "exhaustive": bool }. src and dst map to lists of string
        vertices in the given model. Backdoor paths are searched for from any vertex in src to any vertex in dst.
        "expect" is a list of lists, where each sublist contains a set of string vertices that constitute a backdoor
        path from some vertex in "src" to some vertex in "dst". This sublist must contain these respective endpoints,
        but the order itself does not matter. An optional value in this dictionary can be "dcf": [], which will be a
        list of string vertices to use as a deconfounding set in the respective path searches. "exhaustive" indicates
        whether "expect" is an exhaustive list of all paths.
    @return: True if all tests are successful, False otherwise, as well as a string message summary.
    """

    for test in test_data["tests"]:

        expect = test["expect"]
        src = test["src"]
        dst = test["dst"]
        dcf = test["dcf"] if "dcf" in test else set()

        try:

            if test["type"] == "backdoor-paths":

                if expect != "failure":
                    expect = list(map(sorted, expect))

                paths = bc.backdoor_paths(src, dst, dcf)
                paths = list(map(sorted, paths))

                if test["exhaustive"] and len(paths) != len(expect):    # coverage: skip
                    return False, f"{len(paths)} found, expected {len(expect)}: {paths} vs. Exp: {expect}"

                if not all(map(lambda p: p in paths, expect)):  # coverage: skip
                    missing = list(filter(lambda p: p not in paths, expect))
                    return False, f"Missing {len(missing)} paths: {missing}"

            elif test["type"] == "independence":

                independent = bc.independent(src, dst, dcf)

                if independent != expect:     # coverage: skip
                    return False, f"{src} -> {dst} | {dcf}: {independent}, expected {expect}"

        except IntersectingSets:

            if expect != "failure":     # coverage: skip
                error = f"Unexpected IntersectingSets exception! {src}, {dst}"
                print_test_result(False, error)
                return False, error

    return True, "Backdoor tests passed."


def backdoor_tests(graph_location: Path) -> (bool, str):
    """
    Run tests on models located in a given directory of graphs, verifying various backdoor paths in the models.
    @param graph_location: a directory containing causal graph models in JSON
    @return: True if all tests are successful, False otherwise
    """

    files = sorted(list(filter(lambda x: x.suffix.lower() == ".yml", test_file_directory.iterdir())))
    assert len(files) > 0, f"Found no backdoor module tests"

    all_successful = True

    for test_file in files:

        with test_file.open("r") as f:
            yml_test_data = load(f)

        graph_filename = yml_test_data["graph_filename"]
        with (graph_location / graph_filename).open("r") as f:
            graph_data = load(f)

        bc = BackdoorController(parse_model(graph_data)["graph"])

        success, msg = model_backdoor_validation(bc, yml_test_data)
        print_test_result(success, msg if not success else f"All tests in {test_file}, {graph_filename} passed")

        if not success:     # coverage: skip
            all_successful = False

    return all_successful, "[Backdoor module passed]" if all_successful else "[Backdoor module encountered errors]"
