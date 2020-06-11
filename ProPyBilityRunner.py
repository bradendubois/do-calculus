#########################################################
#                                                       #
#   ProPyBilityRunner.py (Name is a Work In Progress)   #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

from probability_structures.ProPyBilityTables import *
from regression_tests.RegressionTesting import *

import os               # Used to list directory contents to select graphs
from config.config_mgr import access

## TODO - Improve the actual relaying of whether the tests passed/failed, whether to proceed/stop

# If set, run any tests before starting up
if access("runRegressionTestsOnLaunch"):
    results = validate()

    if not results[0] and access("outputRegressionResults") == "failure":
        print(results)

    if not results[0] and access("exitIfRegressionFailure"):
        exit(-1)

# Does the directory of graphs exist?
if os.path.isdir(access("graph_file_folder")):

    # The default file to look for
    graph_file = "causal_graph.json"

    # Find all JSON files in that directory
    files = sorted([file_name for file_name in os.listdir(access("graph_file_folder")) if file_name.endswith(".json")])

    # Only one file, just select it
    if len(files) == 1:
        graph_file = files[0]

    # Multiple files, list them and get a selection
    else:
        print("Files located in:", access("graph_file_folder"))
        for file_index in range(len(files)):
            print("  ", str(file_index+1) + ")", files[file_index])
        print("  ", str(len(files)+1) + ") Exit")

        selection = input("Selection: ")
        while not selection.isdigit() and 1 <= int(selection) <= len(files) + 1:
            selection = input("Selection: ")

        if selection == str(len(files)+1):
            exit(0)

        graph_file = files[int(selection) - 1]

    print("\nLoading:", graph_file, "\n")
    CG = CausalGraph(access("graph_file_folder") + "/" + graph_file)

# No directory, load whatever default is specified in the Causal Graph
else:
    # Specify a path to a graph file if desired
    CG = CausalGraph()

# Start the software
CG.run()
