import itertools
from os import listdir
from os.path import dirname, abspath
from yaml import safe_load as load

from src.validation.test_util import print_test_result

from src.probability.structures.BackdoorController import BackdoorController
from src.util.ModelLoader import parse_new_model

test_file_directory = dirname(abspath(__file__)) + "/test_files"


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

        expected_paths = list(map(sorted, test["expect"]))

        paths = []
        for s, t in itertools.product(test["src"], test["dst"]):
            paths.extend(bc.backdoor_paths_pair(s, t, test["dcf"] if "dcf" in test else {}))

        # Sort each path to improve some sor
        paths = list(map(sorted, paths))

        if test["exhaustive"] and len(paths) != len(expected_paths):
            return False, f"{len(paths)} found, but expected {len(expected_paths)}: {paths} vs. Exp: {expected_paths}"

        if not all(map(lambda p: p in paths, expected_paths)):
            missing = list(filter(lambda p: p not in paths, expected_paths))
            return False, f"Missing {len(missing)} paths: {missing}"

    return True, "Backdoor tests passed."


def backdoor_tests(graph_location: str) -> (bool, str):
    """
    Run tests on models located in a given directory of graphs, verifying various backdoor paths in the models.
    @param graph_location: a directory containing causal graph models in JSON
    @return: True if all tests are successful, False otherwise
    """

    files = sorted(list(filter(lambda x: x.endswith(".yml"), listdir(test_file_directory))))
    all_successful = True

    # TODO - Threading ? Good for inference tests but shouldn't take too long here

    for test_file in files:

        with open(f"{test_file_directory}/{test_file}") as f:
            yml_test_data = load(f)

        graph_filename = yml_test_data["graph_filename"]
        with open(f"{graph_location}/{graph_filename}") as f:
            graph_data = load(f)

        bc = BackdoorController(parse_new_model(graph_data)["graph"])

        success, msg = model_backdoor_validation(bc, yml_test_data)
        print_test_result(success, msg if not success else f"All tests in {test_file}, {graph_filename} passed")

        if not success:
            all_successful = False

    return all_successful, "[Backdoor module passed]" if all_successful else "[Backdoor module encountered errors]"
