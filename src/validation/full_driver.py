# TODO - Run all the tests involved in the entire testing suite - implement threading for that
from src.validation.backdoors.backdoor_path_tests import backdoor_tests
from src.validation.inference.inference_tests import inference_tests
from src.validation.shpitser.shpitser_tests import shpitser_tests


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_test_result(success: bool, msg: str):
    """
    Print a test result to standard out, with a header marking the success of the test
    @param success: bool; True if the test was successful, False otherwise
    @param msg: string; Any arbitrary message returned by the test
    """
    color = bcolors.OKGREEN if success else bcolors.WARNING
    print(f"[{color}{success}{bcolors.ENDC}]: {msg}")


def run_all_tests() -> bool:
    """
    Run all the tests for each of the individual components of the software (the basic inference engine, backdoor paths,
    as well as shpitser).
    @postcondition Output of all tests is printed to standard output
    @return: True if all tests are successful, False otherwise
    """

    graph_location = "src/graphs/full"

    inference_bool, inference_msg = inference_tests(graph_location)
    backdoor_bool, backdoor_msg = backdoor_tests(graph_location)
    shpitser_bool, shpitser_msg = shpitser_tests(graph_location)

    print(inference_msg)

    return all([inference_bool, backdoor_bool, shpitser_bool])
