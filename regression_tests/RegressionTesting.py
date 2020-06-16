#########################################################
#                                                       #
#   Regression Tests                                    #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

import os

from probability_structures.CausalGraph import *
from config.config_mgr import *

# Default regression test directory
regression_test_directory = "regression_tests/test_files"


def create_outcomes(*outcome_statements):
    return [Outcome(*outcome.split("=")) for outcome in outcome_statements]


def within_precision(a: float, b: float, decimals: int) -> bool:
    return abs(a - b) < 1 / (10 ** decimals)


def run_test_file(test_file: str) -> (bool, str):

    # Load the test file
    with open(regression_test_directory + "/" + test_file) as f:
        loaded_test_file = json.load(f)

    # Load the Causal Graph of the given file
    causal_graph = CausalGraph("causal_graphs/" + loaded_test_file["test_file"])
    causal_graph.silent_computation = not output_regression_computation()

    # Independent of tests, ensure that the sum of all probabilities of any variable is 1.0.
    for variable in causal_graph.variables:

        total = 0.0
        for outcome in causal_graph.variables[variable].outcomes:
            result = causal_graph.probability([Outcome(variable, outcome)], [])
            total += result
        assert within_precision(total, 1.0, 4), variable + " does not sum to 1.0 across its outcomes."

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
                body = []
                if len(args) > 1:
                    body = create_outcomes(*args[1].split(","))

                result = causal_graph.probability(head, body)
                expected = test["expected_result"]

                # print(result, expected)

                assert within_precision(result, expected, 5), str(result) + " did not match expected: " + str(expected)

            if test["type"] == "summation":
                total = 0.0
                for arg_set in args:
                    head = create_outcomes(*arg_set[0].split(","))
                    body = []
                    if len(arg_set) > 1:
                        body = create_outcomes(*arg_set[1].split(","))

                    result = causal_graph.probability(head, body)
                    total += result

                expected = test["expected_result"]
                assert within_precision(total, expected, 4), str(total) + " not summing to " + str(expected) + "."

            if test["type"] == "determinism":
                results = []
                head = create_outcomes(*args[0].split(","))
                body = []
                if len(args) > 1:
                    body = create_outcomes(*args[1].split(","))

                for i in range(access("defaultRegressionRepetition")):
                    result = causal_graph.probability(head, body)
                    if result not in results:
                        results.append(result)
                assert len(results) == 1, "Repeated tests yielding multiple results."

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

    # Output a header on regression tests being run if toggled
    if output_regression_computation():
        print("\n" + "*" * 10 + " Regression Tests Beginning " + "*" * 10 + "\n")

    # Run each testing file
    for test_file in files:

        results = run_test_file(test_file)
        if not results[0]:
            return False, test_file + " has failed, with error: " + results[1]

    # Output a footer on regression tests being run if toggled
    if output_regression_computation():
        print("\n" + "*" * 10 + " Regression Tests Completed " + "*" * 10 + "\n")

    return True, "All Tests Passed."
