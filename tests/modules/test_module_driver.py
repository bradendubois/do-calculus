from .backdoors.backdoor_path_tests import backdoor_tests
from .inference.inference_tests import inference_tests
from .shpitser.shpitser_tests import shpitser_tests

from ..test_driver import graphs, print_test_result


def test_backdoor_module() -> bool:
    backdoor_bool, backdoor_msg = backdoor_tests(graphs)
    assert backdoor_bool, backdoor_msg
    print_test_result(backdoor_bool, backdoor_msg)
    return backdoor_bool


def test_inference_module() -> bool:
    inference_bool, inference_msg = inference_tests(graphs)
    assert inference_bool, inference_msg
    print_test_result(inference_bool, inference_msg)
    return inference_bool


def test_shpitser_module() -> bool:
    shpitser_bool, shpitser_msg = shpitser_tests(graphs)
    assert shpitser_bool, shpitser_msg
    print_test_result(shpitser_bool, shpitser_msg)
    return shpitser_bool
