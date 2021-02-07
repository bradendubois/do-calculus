# TODO - Run all the tests involved in the entire testing suite - implement threading for that
from src.validation.backdoors.backdoor_path_tests import backdoor_tests
from src.validation.inference.inference_tests import inference_tests
from src.validation.shpitser.shpitser_tests import shpitser_tests

from src.validation.test_util import print_test_result


def run_all_tests(extreme=False) -> bool:
    """
    Run all the tests for each of the individual components of the software (the basic inference engine, backdoor paths,
    as well as shpitser).
    @param extreme: bool; whether or not to run additional tests on generated models; this may increase testing time
        substantially.
    @postcondition Output of all tests is printed to standard output
    @return: True if all tests are successful, False otherwise
    """

    graph_location = "src/graphs/full"
    generated_location = "src/graphs/generated"

    inference_bool, inference_msg = inference_tests(graph_location)
    backdoor_bool, backdoor_msg = backdoor_tests(graph_location)
    shpitser_bool, shpitser_msg = shpitser_tests(graph_location)

    print_test_result(inference_bool, inference_msg)
    print_test_result(backdoor_bool, backdoor_msg)
    print_test_result(shpitser_bool, shpitser_msg)

    if extreme:

        print("Additional tests beginning...")

        extreme_inference_bool, extreme_inference_msg = inference_tests(generated_location)
        print_test_result(extreme_inference_bool, extreme_inference_msg)
        inference_bool = inference_bool and extreme_inference_bool

    return all([inference_bool, backdoor_bool, shpitser_bool])
