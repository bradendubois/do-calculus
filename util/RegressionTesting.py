#########################################################
#                                                       #
#   Regression Tests                                    #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

from datetime import datetime

from probability_structures.CausalGraph import *
from probability_structures.VariableStructures import *
from util.ProbabilityExceptions import *
from util.parsers.GraphLoader import parse_graph_file_data


def create_head_and_body(head_and_body: list) -> tuple:
    """
    Create the head and body for a probability test
    :param head_and_body: A list, of one/two strings, which are split into Outcomes
    :return: a tuple (head, body)
    """
    head = parse_outcomes_and_interventions(head_and_body[0])
    body = []
    if len(head_and_body) > 1:
        body = parse_outcomes_and_interventions(head_and_body[1])
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
    """
    The main test driver that will run a test file, all the tests in it, plus a few identities
    :param test_file: The exact name of a test file located in the "regression_directory".
    :return: A tuple (success_boolean, success_message) indicating success, or failure and error message.
    """

    # Load the test file
    with open(root + "/" + access("regression_directory") + "/" + test_file) as f:
        loaded_test_file = json.load(f)

    # Default location assumed unless specified
    directory = root + "/" + access("graph_file_folder")
    if "file_directory" in loaded_test_file:
        directory = loaded_test_file["file_directory"]

    # Ensure the file exists
    file_path = directory + "/" + loaded_test_file["test_file"]
    if not os.path.isfile(file_path):
        return False, "Unexpected: Graph file " + loaded_test_file["test_file"] + " not found."
    parsed = parse_graph_file_data(file_path)

    # Load the Causal Graph of the given file
    try:
        causal_graph = CausalGraph(**parsed)
    except Exception as e:
        return False, "Unexpected error in loading: " + loaded_test_file["test_file"] + ": " + str(e.args)

    # Independent of tests, ensure that the sum of all probabilities of any variable is 1.0.
    for variable in causal_graph.variables:

        # Skip variables that rely on functions rather than tables
        if variable in causal_graph.functions:
            continue

        try:
            total = 0.0
            for outcome in causal_graph.variables[variable].outcomes:
                result = causal_graph.probability_query([Outcome(variable, outcome)], [])
                total += result

            assert within_precision(total, 1.0), variable + " does not sum to 1.0 across its outcomes."

        # Indicates an invalid table, missing some row, etc.
        except MissingTableRow as e:
            return False, "[ERROR: " + test_file + "]: Invalid table for the graph." + str(e)

        # Didn't match the expected total
        except AssertionError as e:
            return False, e.args

    # Run each test
    for test in loaded_test_file["tests"]:

        # Load any arguments necessary for the test
        args = test["args"]

        # TODO - This limits the kinds of tests possible. Add a kind of flag indicating tests that
        #   SHOULD crash. Raise a DidNotCrashWhenShould exception.

        # Checking "test_type" determines how to proceed
        try:

            # Simply compare a "given/expected" probability against one calculated by the CG
            if test["type"] == "probability":

                # Construct a list of "Outcomes" from the given args
                head, body = create_head_and_body(args)

                result = causal_graph.probability_query(head, body)
                expected = test["expected_result"]

                assert within_precision(result, expected), str(result) + " did not match expected: " + str(expected)

            # Essentially made obsolete by the identity checking above; ensure multiple tests sum to some given total
            if test["type"] == "summation":

                total = 0.0
                for arg_set in args:
                    # Construct a list of "Outcomes" from the given args
                    head, body = create_head_and_body(arg_set)
                    result = causal_graph.probability_query(head, body)
                    total += result

                expected = test["expected_result"]
                assert within_precision(total, expected), str(total) + " not summing to " + str(expected)

            # Ensure that some given test always only returns 1 value; does not require an "expected", but rather is
            #   a means of error-checking, ensuring that the random ordering of sets does not interfere with the CG
            if test["type"] == "determinism":

                only_result = None    # Begin with a sentinel value
                head, body = create_head_and_body(args)     # Construct a list of "Outcomes" from the given args

                # Set ordering is a property "laid out" at runtime; if we create various different CGs, the ordering
                #   is likely to change between CGs, which could lead to said inconsistencies
                for i in range(access("default_regression_repetition")):

                    parsed = parse_graph_file_data(directory + "/" + loaded_test_file["test_file"])
                    determinism_cg = CausalGraph(**parsed)
                    result = determinism_cg.probability_query(head, body)

                    if only_result is None:     # Storing the first result calculated
                        only_result = result

                    # If the results differ by a significant amount, we consider it a "different value"
                    assert within_precision(only_result, result), "Repeated tests yielding multiple results."

            # Ensure the detection of a "feedback loop" in function-based variables that would devolve into an
            #   infinite loop/stack overflow
            if test["type"] == "feedback_loop":

                try:
                    # This should raise a FunctionFeedbackLoop exception
                    causal_graph.probability_function_query(*causal_graph.functions[args])
                    raise ExceptionNotFired("A feedback loop in " + args + " was not detected.")

                # Awesome if we get this
                except FunctionFeedbackLoop:
                    pass

            # Ensure that every result from the list of queries is the same
            if test["type"] == "equivalence":

                # Start with some sentinel value
                only_result = None

                # Compute with every nested query
                for arg_set in args:

                    # Compute
                    head, body = create_head_and_body(arg_set)
                    result = causal_graph.probability_query(head, body)

                    # Store and/or compare
                    if only_result is None:
                        only_result = result
                    assert within_precision(only_result, result), "Not all queries yielded the same value."

        # Indicates an invalid table, missing some row, etc.
        except MissingTableRow as e:
            return False, "[ERROR: " + test["name"] + "]: Invalid table for the graph." + str(e)

        # ExceptionNotFired indicates an exception *should* have been raised but wasn't
        except ExceptionNotFired as e:
            return False, "[ERROR: " + test["name"] + "]: " + str(e)

        # AssertionErrors indicate the wrong response
        except AssertionError as e:
            return False, "[ERROR: " + test["name"] + "]: " + str(e)

        # All other exceptions indicate that the test crashed when it shouldn't
        except Exception as e:
            return False, "[CRASH: " + test["name"] + "]: " + str(e)

    return True, "All tests in " + test_file + " passed."


def run_full_regression_suite() -> (bool, str):
    """
    Run all regression tests
    :return: A tuple (success boolean, return message) representing Failure+Error or Success+NoError
    """

    # Fail / Exit if there is no directory found
    if not os.path.isdir(access("regression_directory")):
        return False, "Cannot locate any regression tests."

    # Find all JSON files in that directory
    files = sorted([file_name for file_name in os.listdir(root + "/" + access("regression_directory")) if file_name.endswith(".json")])

    # Running tests but no files?
    if len(files) == 0 and access("run_regression_tests_on_launch"):
        io.write("ERROR: Regression tests enabled, but no test files found.")

    # Output a header on regression tests being run if toggled
    if access("output_regression_test_computation"):
        io.write("\n" + "*" * 10 + " Regression Tests Beginning " + "*" * 10 + "\n")
    # Disable the IO/Logger to console if regression test results not set to output
    else:
        io.disable_console()

    # Open a regression file to log to if enabled
    if access("log_all_regression_computation"):

        log_dir = access("regression_log_subdirectory")

        # Create the logging directory if it doesn't exist
        if not os.path.isdir(access("logging_directory") + "/" + log_dir):
            os.makedirs(access("logging_directory") + "/" + log_dir)

        log_file = log_dir + "/" + "r" + datetime.now().strftime("%Y%m%d_%H-%M-%S")
        io.open(log_file)
        io.lock_stream_switch = True    # Ensure the inference engine doesn't switch file streams

    # Store all results from each file, so that we could have an error in one file but still test subsequent ones
    all_regression_results = []

    # Run each testing file
    for test_file in files:
        results = run_test_file(test_file)
        if not results[0]:
            all_regression_results.append((False, test_file + " has failed, with error: " + str(results[1])))
        else:
            all_regression_results.append(results)

    # Output a footer on regression tests being run if toggled
    if access("output_regression_test_computation"):
        io.write("\n" + "*" * 10 + " Regression Tests Completed " + "*" * 10 + "\n")

    # Enable IO if it was disabled; close any regression file being written to
    io.enable_console()
    io.lock_stream_switch = False
    io.close()

    # Add the "summary" value
    # If there is at least one error...
    if any(not item[0] for item in all_regression_results):
        all_regression_results.append((False, "There were errors."))
    else:
        all_regression_results.append((True, "All Tests Passed."))

    return all_regression_results
