#########################################################
#                                                       #
#   Graph Loader                                        #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Here, we can simply take a graph file and load it, isolating this code and reducing the Causal Graph filesize

from json import load as json_load
from yaml import safe_load as yaml_load

from os import path

from ..probability.structures.ConditionalProbabilityTable import ConditionalProbabilityTable
from ..probability.structures.Graph import Graph
from ..probability.structures.VariableStructures import *


def parse_graph_file_data(filename: str or dict) -> dict:
    """
    Load, read, and parse a graph file for use in Causal Graphs, etc.
    :param filename: The exact path to the file
    :return: A dictionary of all data needed to construct a Causal Graph
    """

    # Ensure the file exists
    if isinstance(filename, str) and not path.isfile(filename):
        print("ERROR: Can't find:", filename)
        raise Exception

    # Load the file, then we parse it
    if isinstance(filename, str):
        with open(filename) as json_file:
            loaded_file = load(json_file)
    else:
        loaded_file = filename

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

    # Set of latent variables
    latent = set()

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

        if "latent" in v and v["latent"]:
            latent.add(name)
            latent.add(variable)

        if determination["type"] == "table":

            # Save that this variable is determined by a table
            variable_determination[name] = "table"
            variable_determination[variable] = "table"

            # Load in the table and construct a CPT
            table = determination["table"]
            cpt = ConditionalProbabilityTable(variable, variable_parents, table)

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
        "graph": graph,
        "latent": latent
    }

    return parsed


def parse_new_model(file: dict or str):

    if isinstance(file, dict):
        data = file

    elif not path.isfile(file):
        print("ERROR: Can't find:", file)
        raise FileNotFoundError

    else:
        load = json_load if file.lower().endswith(".json") else yaml_load

        with open(file,  "r") as f:
            data = load(f)

    # Maps string name to the Variable object instantiated
    variables = dict()

    # Maps string name *and* corresponding Variable to a list of outcome values
    outcomes = dict()

    # Maps to corresponding tables
    tables = dict()

    # Set of latent variables
    latent = set()

    for name, detail in data["model"].items():

        # Load the relevant data to construct a Variable
        v_outcomes = detail["outcomes"] if "outcomes" in detail else []
        v_parents = detail["parents"] if "parents" in detail else []

        # Create a Variable object
        variable = Variable(name, v_outcomes, v_parents)

        # Lookup the object by its name
        variables[name] = variable

        # Store by both the Variable object as well as its name, for ease of access
        outcomes[name] = v_outcomes
        outcomes[variable] = v_outcomes

        if "latent" in detail and detail["latent"]:
            latent.add(name)
            latent.add(variable)

        # Load in the table and construct a CPT
        table = detail["table"]
        cpt = ConditionalProbabilityTable(variable, v_parents, table)

        # Map the name/variable to the table
        tables[name] = cpt
        tables[variable] = cpt

    v = set(variables.keys())
    e = set()
    for child in variables.keys():
        e.update(list(map(lambda parent: (parent, child), variables[child].parents)))
    graph = Graph(v, e)

    # Store all the different dictionaries of data as one large dictionary
    parsed = {
        "variables": variables,
        "outcomes": outcomes,
        "tables": tables,
        "graph": graph,
        "latent": latent
    }

    return parsed
