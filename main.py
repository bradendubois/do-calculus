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
import json
import os
from sys import argv

from src.REPL import run_repl

# TODO - Examine if necessary after re-works; should always set cwd to root of file itself
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#######################################
#             Parse Input             #
#######################################

run_debug = len(argv) >= 2 and argv[1].lower() in ["validate", "debug", "test"]

#######################################
#     Test Software (if specified)    #
#######################################

if run_debug:
    from tests.RegressionTesting import run_full_regression_suite

    # List of (success_boolean, message) tuples returned
    # Last item will be a summary "(false, "there were errors")" / "(true, "no errors")"
    results = run_full_regression_suite()
    success, summary = results[-1]
    print("\n".join(map(str, results)))

#######################################
#                 REPL                #
#######################################

run_repl()
