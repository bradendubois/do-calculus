#########################################################
#                                                       #
#   ProPyBilityRunner.py (Name is a Work In Progress)   #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

from probability_structures.ProPyBilityTables import *
import os               # Used to list directory contents to select graphs

# Default Graph Folder
graph_file_folder = "causal_graphs"

# Does the directory of graphs exist?
if os.path.isdir(graph_file_folder):

    # The default file to look for
    graph_file = "causal_graph.json"

    # Find all JSON files in that directory
    files = sorted([file_name for file_name in os.listdir(graph_file_folder) if file_name.endswith(".json")])

    # Only one file, just select it
    if len(files) == 1:
        graph_file = files[0]

    # Multiple files, list them and get a selection
    else:
        print("Files located in:", graph_file_folder)
        for file_index in range(len(files)):
            print("  ", str(file_index+1) + ")", files[file_index])

        file = input("Selection: ")
        while not file.isdigit() and 1 <= int(file) <= len(files):
            file = input("Selection: ")

        graph_file = files[int(file)-1]

    print("\nLoading:", graph_file, "\n")
    CG = CausalGraph(graph_file_folder + "/" + graph_file)

# No directory, load whatever default is specified in the Causal Graph
else:
    # Specify a path to a graph file if desired
    CG = CausalGraph()

# Start the software
CG.run()
