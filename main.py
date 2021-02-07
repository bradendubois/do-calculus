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

# TODO - Examine if necessary after re-works; should always set cwd to root of file itself
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#######################################
#             Parse Input             #
#######################################

run_debug = len(argv) >= 2 and argv[1].lower() == "debug"

#######################################
#     Test Software (if specified)    #
#######################################

if run_debug:
    from src.validation.full_driver import run_all_tests
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
