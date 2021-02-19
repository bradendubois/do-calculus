from yaml import load
from os import listdir

from src.probability.structures.CausalGraph import *
from src.probability.structures.VariableStructures import *
from src.util.ProbabilityExceptions import *
from src.util.ModelLoader import parse_graph_file_data, parse_new_model
from src.validation.test_util import print_test_result


def within_precision(a: float, b: float) -> bool:
    """
    Check whether two values differ by an amount less than some number of digits of precision
    @param a: The first value
    @param b: The second value
    @return: True if the values are within the margin of error acceptable, False otherwise
    """
    return abs(a - b) < 1 / (10 ** access("regression_levels_of_precision"))


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
        except ProbabilityIndeterminableException:
            return False, f"Probability indeterminable for the graph. Variable {variable}"

        # Indicates an invalid table, missing some row, etc.
        except MissingTableRow as e:
            return False, f"Invalid table for the graph: {e}"

        # Didn't match the expected total
        except AssertionError as e:
            return False, f"Failed assertion: {e}"

    return True, "Basic tests passed."


def inference_tests(graph_location: str) -> (bool, str):
    """
    Run tests on all models located in a given directory of graphs, verifying the probabilities in the model.
    @param graph_location: A string path to a directory containing any number of causal graph JSON files
    @return: True if all tests are successful, False otherwise, along with a string summary message.
    """

    files = sorted(list(filter(lambda x: x.endswith(".yml"), listdir(graph_location))))
    all_successful = True

    # TODO - Threading to handle all the tests

    for test_file in files:

        with open(graph_location + "/" + test_file) as f:
            yml_model = load(f)

        parsed_model = parse_new_model(yml_model)
        causal_graph = CausalGraph(**parsed_model)

        success, msg = model_inference_validation(causal_graph)
        print_test_result(success, msg if not success else f"All tests in {test_file} passed")

        if not success:
            all_successful = False

    return all_successful, "Inference module passed" if all_successful else "Inference module encountered errors"
