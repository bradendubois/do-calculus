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
            print("\nFiles located in:", access("graph_file_folder"))
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

            print("\nLoading:", graph_file, "\n")
            CausalGraph(access("graph_file_folder") + "/" + graph_file).run()

# No directory, load whatever default is specified in the Causal Graph
else:
    # Specify a path to a graph file if desired
    CG = CausalGraph()

    # Start the software
    CG.run()
