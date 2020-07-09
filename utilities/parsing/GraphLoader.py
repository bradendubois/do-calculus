#########################################################
#                                                       #
#   Graph Loader                                        #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Here, we can simply take a graph file and load it, isolating this code and reducing the Causal Graph filesize

import os

from probability_structures.ConditionalProbabilityTable import *
from probability_structures.Graph import Graph
from probability_structures.VariableStructures import *
from utilities.IO_Logger import *


def parse_graph_file_data(filename: str) -> dict:
    """
    Load, read, and parse a graph file for use in Causal Graphs, etc.
    :param filename: The exact path to the file
    :return: A dictionary of all data needed to construct a Causal Graph
    """

    # Ensure the file exists
    if not os.path.isfile(filename):
        io.write("ERROR: Can't find:", filename)
        raise Exception

    # Load the file, then we parse it
    with open(filename) as json_file:
        loaded_file = json.load(json_file)

    # Maps string name to the Variable object instantiated
    variables = dict()

    # Maps string name *and* corresponding variable to a list of outcome values
    outcomes = dict()

    # Maps to "table" or "function", indicating how it is calculated
    variable_determination = dict()

    # Maps to corresponding tables
    tables = dict()

    # Maps to corresponding functions
    functions = dict()

    for v in loaded_file["variables"]:

        # Load the relevant data to construct a Variable
        name = v["name"]
        variable_outcomes = v["outcomes"] if "outcomes" in v else []
        variable_parents = v["parents"] if "parents" in v else []

        # Create a fancy Variable object
        variable = Variable(name, variable_outcomes, variable_parents)

        # Lookup the object by its name
        variables[name] = variable

        # Store by both the Variable object as well as its name, for ease of access
        outcomes[name] = variable_outcomes
        outcomes[variable] = variable_outcomes

        # Is the variable determined by a function or direct tables?
        determination = v["determination"]
        determination_type = determination["type"]

        if determination["type"] == "table":

            # Save that this variable is determined by a table
            variable_determination[name] = "table"
            variable_determination[variable] = "table"

            # Load in the table and construct a CPT
            table = determination["table"]
            cpt = ConditionalProbabilityTable(variable, table["given"], table["rows"])

            # Map the name/variable to the table
            tables[name] = cpt
            tables[variable] = cpt

        elif determination_type == "function":

            # Save that this variable is determined by a function
            variable_determination[name] = "function"
            variable_determination[variable] = "function"

            # Map the name/variable to the function
            functions[name] = determination["function"]
            functions[variable] = determination["function"]

        else:
            print("ERROR; Variable", name, "determination cannot be found.")
            exit(-1)

    v = set([v for v in variables])
    e = set().union(*[[(parent, child) for parent in variables[child].parents] for child in variables])
    graph = Graph(v, e)

    # Store all the different dictionaries of data as one large dictionary
    parsed = {
        "variables": variables,
        "outcomes": outcomes,
        "determination": variable_determination,
        "tables": tables,
        "functions": functions,
        "v": v,
        "e": e,
        "graph": graph
    }

    return parsed
