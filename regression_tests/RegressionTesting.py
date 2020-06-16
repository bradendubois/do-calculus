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


def create_outcomes(*outcome_statements):
    """
    Create a list of Outcome objects
    :param outcome_statements: Any number of strings "VARIABLE = OUTCOME"
    :return: A list of Outcome objects
    """
    return [Outcome(*outcome.split("=")) for outcome in outcome_statements]


def create_head_and_body(head_and_body: list) -> tuple:
    """
    Create the head and body for a probability test
    :param head_and_body: A list, of one/two strings, which are split into Outcomes
    :return: a tuple (head, body)
    """
    head = create_outcomes(*head_and_body[0].split(","))
    body = []
    if len(head_and_body) > 1:
        body = create_outcomes(*head_and_body[1].split(","))
    return head, body


def within_precision(a: float, b: float) -> bool:
    """
    Check whether two values differ by an amount less than some number of digits of precision
    :param a: The first value
    :param b: The second value
    :return: True if the values are within the margin of error acceptable, False otherwise
    """
    return abs(a - b) < 1 / (10 ** access("regression_levels_of_precision"))


def run_test_file(test_file: str) -> (bool, str):

    # Load the test file
    with open(access("regression_directory") + "/" + test_file) as f:
        loaded_test_file = json.load(f)

    # Load the Causal Graph of the given file
    causal_graph = CausalGraph(access("graph_file_folder") + "/" + loaded_test_file["test_file"])
    causal_graph.silent_computation = not access("output_computation_steps")

    # Independent of tests, ensure that the sum of all probabilities of any variable is 1.0.
    for variable in causal_graph.variables:

        total = 0.0
        for outcome in causal_graph.variables[variable].outcomes:
            result = causal_graph.probability([Outcome(variable, outcome)], [])
            total += result

        try:
            assert within_precision(total, 1.0), variable + " does not sum to 1.0 across its outcomes."
        except AssertionError as e:
            return False, e.args

    # Run each test
    for test in loaded_test_file["tests"]:

        # Load any arguments necessary for the test
        args = test["args"]

        # TODO - This limits the kinds of tests possible. Add a kind of flag indicating tests that
        #   SHOULD crash. Raise a DidNotCrashWhenShould exception.

        try:
            # Only supporting probability tests currently, but checking "test_type" determines how to proceed
            if test["type"] == "probability":

                # Construct a list of "Outcomes" from the given args
                head, body = create_head_and_body(args)

                result = causal_graph.probability(head, body)
                expected = test["expected_result"]

                assert within_precision(result, expected), str(result) + " did not match expected: " + str(expected)

            if test["type"] == "summation":
                total = 0.0
                for arg_set in args:

                    # Construct a list of "Outcomes" from the given args
                    head, body = create_head_and_body(arg_set)

                    result = causal_graph.probability(head, body)
                    total += result

                expected = test["expected_result"]
                assert within_precision(total, expected), str(total) + " not summing to " + str(expected) + "."

            if test["type"] == "determinism":
                results = []

                # Construct a list of "Outcomes" from the given args
                head, body = create_head_and_body(args)

                for i in range(access("regression_determinism_repetition")):
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


def validate_all_regression_tests() -> (bool, str):
    """
    Run all regression tests
    :return: A tuple (success boolean, return message) representing Failure+Error or Success+NoError
    """

    # Fail / Exit if there is no directory found
    if not os.path.isdir(access("regression_directory")):
        return False, "Cannot locate any regression tests."

    # Find all JSON files in that directory
    files = sorted([file_name for file_name in access("regression_directory") if file_name.endswith(".json")])

    # Output a header on regression tests being run if toggled
    if access("output_regression_computation"):
        print("\n" + "*" * 10 + " Regression Tests Beginning " + "*" * 10 + "\n")

    # Run each testing file
    for test_file in files:

        results = run_test_file(test_file)
        if not results[0]:
            return False, test_file + " has failed, with error: " + results[1]

    # Output a footer on regression tests being run if toggled
    if access("output_regression_computation"):
        print("\n" + "*" * 10 + " Regression Tests Completed " + "*" * 10 + "\n")

    return True, "All Tests Passed."
