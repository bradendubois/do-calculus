#########################################################
#                                                       #
#   Regression Tests                                    #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

from os import listdir

from src.probability.structures.CausalGraph import *
from src.probability.structures.VariableStructures import *
from src.util.ProbabilityExceptions import *
from src.util.ModelLoader import parse_graph_file_data
from src.validation.full_driver import print_test_result


def within_precision(a: float, b: float) -> bool:
    """
    Check whether two values differ by an amount less than some number of digits of precision
    :param a: The first value
    :param b: The second value
    :return: True if the values are within the margin of error acceptable, False otherwise
    """
    return abs(a - b) < 1 / (10 ** access("regression_levels_of_precision"))


def model_inference_validation(cg: CausalGraph):
    """
    Validate all distributions in the given Causal Graph
    @param cg: a Causal Graph model
    @return: True if the sum of probabilities of each outcome equals 1 for each variable, False otherwise
    """

    for variable in cg.variables:

        try:
            total = sum(cg.probability_query({Outcome(variable, outcome)}, {}) for outcome in cg.outcomes[variable])
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


def inference_tests(graph_location) -> bool:
    """
    Load and run all tests on all models located in a given directory of graphs
    @param graph_location: A string path to a directory containing any number of causal graph JSON files
    @return: True if all tests are successful, False otherwise
    """

    files = sorted(list(filter(lambda x: x.endswith(".json"), listdir(graph_location))))
    all_successful = True

    # TODO - Threading to handle all the tests

    for test_file in files:

        with open(access("regression_directory") + "/" + test_file) as f:
            json_model = json.load(f)

        parsed_model = parse_graph_file_data(json_model)
        causal_graph = CausalGraph(**parsed_model)

        success, msg = model_inference_validation(causal_graph)
        print_test_result(success, msg)

        if not success:
            all_successful = False

    return all_successful