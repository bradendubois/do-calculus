#########################################################
#                                                       #
#   main.py / Probability Runner                        #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

from probability_structures.CausalGraph import *
from regression_tests.RegressionTesting import *

import os               # Used to list directory contents to select graphs
from config.config_mgr import *

# If set, run any tests before starting up
if access("run_regression_tests_on_launch"):

    # (success_boolean, message) tuple returned
    results = validate_all_regression_tests()

    # Output results if config settings specify it
    if not results[0] and access("output_regression_results") == "failure":
        print(results)
    elif access("output_regression_results") == "always":
        print(results)

    # Config settings do allow us to continue even if tests fail
    if not results[0] and access("exit_if_regression_failure"):
        exit(-1)

# Does the directory of graphs exist?
if os.path.isdir(access("graph_file_folder")):

    # Find all JSON files in that directory
    files = sorted([file_name for file_name in os.listdir(access("graph_file_folder")) if file_name.endswith(".json")])
    longest_file_length = max(len(file) for file in files)

    # Only one file, just select it
    if len(files) == 1:
        graph_file = files[0]

    # Multiple files, list them and get a selection
    else:
        print("Files located in:", access("graph_file_folder"))
        for file_index in range(len(files)):

            # Show the name as a preview/reminder, if given
            name = ""
            with open(access("graph_file_folder") + "/" + files[file_index]) as f:
                # Load the file and if there is a name, we can fancy up the output
                loaded = json.load(f)
                if "name" in loaded:
                    name = " " * (longest_file_length - len(files[file_index])) + "- " + loaded["name"]
            print("  ", str(file_index+1) + ")", files[file_index], name)
        print("  ", str(len(files)+1) + ") Exit")

        selection = input("Selection: ")
        while not selection.isdigit() or not 1 <= int(selection) <= len(files) + 1:
            selection = input("Selection: ")

        # Last selection is always to exit
        if selection == str(len(files)+1):
            exit(0)

        graph_file = files[int(selection) - 1]

    print("\nLoading:", graph_file)
    CG = CausalGraph(access("graph_file_folder") + "/" + graph_file)

# No directory, load whatever default is specified in the Causal Graph
else:
    # Specify a path to a graph file if desired
    CG = CausalGraph()

# Start the software
CG.run()
