# TODO - Run all the tests involved in the entire testing suite - implement threading for that

from src.validation.backdoors.backdoor_path_tests import backdoor_tests
from src.validation.inference.inference_tests import inference_tests
from src.validation.shpitser.shpitser_tests import shpitser_tests

from src.validation.test_util import print_test_result

graph_location = "src/graphs/full"
generated_location = "src/graphs/generated"

# api

def test_api_backdoor_paths():
    ...


def test_api_deconfounding_sets():
    ...


def test_api_joint_distribution_table():
    ...


def test_api_probability_query():
    ...


# config - TODO


# graphs

def test_sum_to():
    ...


def test_generate_distribution():
    ...


def test_cycle():
    ...


def test_longest():
    ...


def test_generate_graph():
    ...


def test_randomized_latent_variables():
    ...

# TODO make model_generator into runnable function

# probability/

# probability/do_calculus - TODO

# probability/shpitser - TODO

# probability/structures


# probability/structures/BackdoorController

def test_backdoor_paths():
    ...


def test_backdoor_paths_pair():
    ...


def test_all_dcf_sets():
    ...


def test_all_paths_cumulative():
    ...


def test_independent():
    ...


# probability/structures/CausalGraph

def test_probability_query():
    ...


# probability/structures/ConditionalProbabilityTable

def test_probability_lookup():
    ...


# probability/structures/Graph

def test_roots():
    ...


def test_parents():
    ...


def test_children():
    ...


def test_ancestors():
    ...


def test_reach():
    ...


def test_disable_outgoing():
    ...


def test_disable_incoming():
    ...


def test_reset_disabled():
    ...


def test_get_topology():
    ...


def test_graph_copy():
    ...


def test_topological_variable_sort():
    ...


def test_descendant_first_sort():
    ...


def test_to_label():
    ...


# probability/structures/Probability_Engine

def test_probability():
    ...


# probability/structures/VariableStructures

def test_outcome():
    ...


def test_variable():
    ...


def test_intervention():
    ...


def test_parse_outcomes_and_interventions():
    ...


# util/

def test_power_set():
    ...


def test_minimal_sets():
    ...


def test_disjoint():
    ...


def test_p_str():
    ...


def test_parse_model():
    ...


def test_output_logger():
    ...


# validation

def test_inference_module() -> bool:
    inference_bool, inference_msg = inference_tests(graph_location)
    assert inference_bool, inference_msg
    print_test_result(inference_bool, inference_msg)
    return inference_bool


def test_backdoor_module() -> bool:
    backdoor_bool, backdoor_msg = backdoor_tests(graph_location)
    assert backdoor_bool, backdoor_msg
    print_test_result(backdoor_bool, backdoor_msg)
    return backdoor_bool


def test_shpitser_module() -> bool:
    shpitser_bool, shpitser_msg = shpitser_tests(graph_location)
    assert shpitser_bool, shpitser_msg
    print_test_result(shpitser_bool, shpitser_msg)
    return shpitser_bool



# TODO - Incorporate into above tests
def run_all_tests(extreme=False) -> bool:
    """
    Run all the tests for each of the individual components of the software (the basic inference engine, backdoor paths,
    as well as shpitser).
    @param extreme: bool; whether or not to run additional tests on generated models; this may increase testing time
        substantially.
    @postcondition Output of all tests is printed to standard output
    @return: True if all tests are successful, False otherwise
    """

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
