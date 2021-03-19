from os.path import dirname, abspath
from pathlib import Path
from yaml import safe_load as load

from do.structures.CausalGraph import CausalGraph, Outcome
from do.structures.VariableStructures import parse_outcomes_and_interventions
from do.util.helpers import within_precision
from do.util.ModelLoader import parse_model
from do.util.ProbabilityExceptions import *

from ..test_util import print_test_result

test_file_directory = Path(dirname(abspath(__file__))) / "test_files"


def model_inference_validation(cg: CausalGraph) -> (bool, str):
    """
    Validate all distributions in the given Causal Graph
    @param cg: a Causal Graph model
    @return: True if the sum of probabilities of each outcome equals 1 for each variable, False otherwise, as well
        as a string message summary.
    """

    for variable in cg.variables:

        try:
            total = sum(cg.probability_query({Outcome(variable, outcome)}, set()) for outcome in cg.outcomes[variable])
            assert within_precision(total, 1.0), f"{variable} does not sum to 1.0 across its outcomes ({total})."

        # Probability failed to compute entirely
        except ProbabilityIndeterminableException:      # coverage: skip
            return False, f"Probability indeterminable for the graph. Variable {variable}"

        # Indicates an invalid table, missing some row, etc.
        except MissingTableRow as e:        # coverage: skip
            return False, f"Invalid table for the graph: {e}"

        # Didn't match the expected total
        except AssertionError as e:     # coverage: skip
            return False, f"Failed assertion: {e}"

    return True, "Basic tests passed."


def inference_tests(graph_location: Path) -> (bool, str):
    """
    Run tests on all models located in a given directory of graphs, verifying the probabilities in the model.
    @param graph_location: A string path to a directory containing any number of causal graph JSON files
    @return: True if all tests are successful, False otherwise, along with a string summary message.
    """

    model_files = sorted(list(filter(lambda x: x.suffix.lower() == ".yml", graph_location.iterdir())))
    test_files = sorted(list(filter(lambda x: x.suffix.lower() == ".yml", test_file_directory.iterdir())))

    assert len(model_files) > 0, "Models not found"
    assert len(test_files) > 0, "Inference test files not found"

    all_successful = True

    for model in model_files:

        with model.open("r") as f:
            yml_model = load(f)

        parsed_model = parse_model(yml_model)
        causal_graph = CausalGraph(**parsed_model)

        success, msg = model_inference_validation(causal_graph)
        print_test_result(success, msg if not success else f"All tests in {model} passed")

        if not success:     # coverage: skip
            all_successful = False

    for test_file in test_files:

        with test_file.open("r") as f:
            yml_test_data = load(f)

        graph_filename = yml_test_data["graph_filename"]
        with (graph_location / graph_filename).open("r") as f:
            graph_data = load(f)

        cg = CausalGraph(**parse_model(graph_data))

        test_file_success = True

        for test in yml_test_data["tests"]:

            head = parse_outcomes_and_interventions(test["head"])
            body = parse_outcomes_and_interventions(test["body"]) if "body" in test else set()

            result = cg.probability_query(head, body)
            expected = test["expect"]

            if expected != "failure" and not within_precision(result, expected):    # coverage: skip
                print_test_result(False, f"Got {result} but expected {expected} in {graph_filename}")
                test_file_success = False

        if test_file_success:
            print_test_result(True, f"All tests in {test_file}|{graph_filename} passed")
        else:   # coverage: skip
            all_successful = False

    return all_successful, "Inference module passed" if all_successful else "Inference module encountered errors"
