#########################################################
#                                                       #
#   Regression Tests                                    #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

import os
import json

from probability_structures.ProPyBilityTables import *

# Default regression test directory
regression_test_directory = "regression_tests/test_files"


def create_outcomes(*outcome_statements):
    return [Outcome(*outcome.split("=")) for outcome in outcome_statements]


def within_precision(a: float, b: float, decimals: int) -> bool:
    return abs(a - b) < 1 ** (-1 * decimals)


def run_test_file(test_file: str) -> (bool, str):

    # Load the test file
    with open(regression_test_directory + "/" + test_file) as f:
        loaded_test_file = json.load(f)

    # Load the Causal Graph of the given file
    causal_graph = CausalGraph("causal_graphs/" + loaded_test_file["test_file"])
    causal_graph.silent_computation = True

    # Run each test
    for test in loaded_test_file["tests"]:

        # Load any arguments necessary for the test
        args = test["args"]

        try:
            # Only supporting probability tests currently, but checking "test_type" determines how to proceed
            if test["type"] == "probability":

                # Construct a list of "Outcomes" from the given args
                # TODO - This limits the kinds of tests possible. Add a kind of flag indicating tests that
                #   SHOULD crash. Raise a DidNotCrashWhenShould exception.

                head = create_outcomes(*args[0].split(","))
                body = create_outcomes(*args[1].split(","))

                result = causal_graph.probability(head, body)
                expected = test["expected_result"]

                assert within_precision(result, expected, 5), str(result) + " did not match expected: " + str(expected)

        # AssertionErrors indicate the wrong response
        except AssertionError as e:
            return False, "[ERROR: " + test["name"] + "]: " + str(e)

        # All other exceptions indicate that the test crashed when it shouldn't
        except Exception as e:
            return False, "[CRASH: " + test["name"] + "]: " + str(e)

    return True, "All tests in " + test_file + "Passed."


def validate() -> (bool, str):

    # Fail / Exit if there is no directory found
    if not os.path.isdir(regression_test_directory):
        return False, "Cannot locate any regression tests."

    # Find all JSON files in that directory
    files = sorted([file_name for file_name in os.listdir(regression_test_directory) if file_name.endswith(".json")])

    # Run each testing file
    for test_file in files:

        results = run_test_file(test_file)
        if not results[0]:
            return False, test_file + " has failed, with error: " + results[1]

    return True, "All Tests Passed."
