#!/usr/bin/env python

#########################################################
#                                                       #
#   main.py                                             #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Main libraries can always be loaded
import os
from sys import argv

from src.REPL import run_repl
from src.validation.backdoors.backdoor_path_tests import backdoor_tests
from src.validation.inference.inference_tests import inference_tests
from test_driver import full_graphs

# TODO - Examine if necessary after re-works; should always set cwd to root of file itself
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#######################################
#             Parse Input             #
#######################################

# TODO - cleaner way of integrating tests with workflow

if len(argv) > 1 and argv[1].lower() == "inference":
    inference_bool, inference_msg = inference_tests(full_graphs)
    assert inference_bool, f"Inference module has failed: {inference_msg}"
    exit(0)

if len(argv) > 1 and argv[1].lower() == "backdoor":
    backdoor_bool, backdoor_msg = backdoor_tests(full_graphs)
    assert backdoor_bool, f"Backdoor module has failed: {backdoor_msg}"
    exit(0)

run_debug = len(argv) >= 2 and argv[1].lower() == "debug"

#######################################
#     Test Software (if specified)    #
#######################################

if run_debug:
    from test_driver import run_all_tests
    from src.validation.test_util import print_test_result

    index = argv.index("debug")
    extreme = len(argv) > index+1 and argv[index+1].lower() == "extreme"

    # Boolean result returned: True if all tests are successful, False otherwise
    success = run_all_tests(extreme)
    print_test_result(success, "[All Tests Passed]" if success else "[Some Errors Occurred]")

#######################################
#                 REPL                #
#######################################

run_repl()
