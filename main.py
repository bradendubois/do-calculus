#!/usr/bin/env python

#########################################################
#                                                       #
#   main.py / Probability Runner                        #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Main libraries can always be loaded
from os import path, listdir
import json

# Only import (from the software itself) the configuration module to see which modules are enabled
from config.config_manager import access

# Update / pull if enabled
if access("github_pull_on_launch"):
    import subprocess
    subprocess.call(["./scripts/git_update.sh"])

# Import the IO Logger *after* potentially updating
from utilities.IO_Logger import io

# If set, run any tests before starting up
if access("run_regression_tests_on_launch"):

    # Import the regression suite
    from utilities.RegressionTesting import run_full_regression_suite

    # List of (success_boolean, message) tuples returned
    # Last item will be a summary "(false, "there were errors")" / "(true, "no errors")"
    results = run_full_regression_suite()

    # Output results if config settings specify it
    if not results[-1][0] and access("output_regression_results") == "failure":
        print("\n".join(str(result) for result in results))
    elif access("output_regression_results") == "always":
        print("\n".join(str(result) for result in results))

    # Config settings do allow us to continue even if tests fail
    if not results[-1][0] and access("exit_if_regression_failure"):
        exit(-1)

# Does the directory of graphs exist?
if path.isdir(access("graph_file_folder")):

    # Import the REPL Driver and Graph Loader libraries
    from probability_structures.REPL_Driver import REPLDriver, user_index_selection
    from utilities.parsing.GraphLoader import parse_graph_file_data

    # Find all JSON files in that directory
    files = sorted([file_name for file_name in listdir(access("graph_file_folder")) if file_name.endswith(".json")])
    longest_file_length = max(len(file) for file in files)

    # Only one file, just select it and exit when done
    if len(files) == 1:
        graph_file = files[0]
        print("\nLoading:", graph_file)
        parsed_contents = parse_graph_file_data(graph_file)
        REPLDriver(parsed_contents).run()

    # Multiple files, list them and get a selection, allow switching
    else:
        while True:

            # Generate the menu options list to present and query
            files_options = []
            for file in files:
                with open(access("graph_file_folder") + "/" + file) as f:
                    single_file = [file]
                    loaded = json.load(f)
                    if "name" in loaded:
                        single_file.append(loaded["name"])
                    files_options.append(single_file)
            files_options.append(["Exit"])

            # Get a selection from the user
            selection = user_index_selection("Files located in: "+access("graph_file_folder"), files_options)

            # Last selection is always to exit
            if selection == len(files_options)-1:
                exit(0)

            graph_file = files[int(selection)]

            print("\nLoading:", graph_file)
            parsed_contents = parse_graph_file_data(access("graph_file_folder") + "/" + graph_file)
            REPLDriver(parsed_contents).run()

# Directory not found
else:
    io.write("Graph File Directory not found.")
