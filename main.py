#!/usr/bin/env python

#########################################################
#                                                       #
#   main.py / Probability Runner                        #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

from utilities.RegressionTesting import *
from config.config_manager import *

# If set, run any tests before starting up
if access("run_regression_tests_on_launch"):

    # List of (success_boolean, message) tuples returned
    # Last item will be a summary "(false, "there were errors")" / "(true, "no errors")"
    results = validate_all_regression_tests()

    # Output results if config settings specify it
    if not results[-1][0] and access("output_regression_results") == "failure":
        print("\n".join(str(result) for result in results))
    elif access("output_regression_results") == "always":
        print("\n".join(str(result) for result in results))

    # Config settings do allow us to continue even if tests fail
    if not results[-1][0] and access("exit_if_regression_failure"):
        exit(-1)

# Does the directory of graphs exist?
if os.path.isdir(access("graph_file_folder")):

    # Find all JSON files in that directory
    files = sorted([file_name for file_name in os.listdir(access("graph_file_folder")) if file_name.endswith(".json")])
    longest_file_length = max(len(file) for file in files)

    # Only one file, just select it and exit when done
    if len(files) == 1:
        graph_file = files[0]
        print("\nLoading:", graph_file)
        CausalGraph(access("graph_file_folder") + "/" + graph_file).run()

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
            CausalGraph(access("graph_file_folder") + "/" + graph_file).run()

# No directory, load whatever default is specified in the Causal Graph
else:
    # Specify a path to a graph file if desired
    CG = CausalGraph()

    # Start the software
    CG.run()
