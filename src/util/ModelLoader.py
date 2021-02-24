from json import load as json_load
from os import path
from yaml import safe_load as yaml_load

from src.probability.structures.ConditionalProbabilityTable import ConditionalProbabilityTable
from src.probability.structures.Graph import Graph
from src.probability.structures.VariableStructures import *


def parse_model(file: dict or str):
    """
    Parse a given model for use within the project, such as to create a CausalGraph
    @param file: a string path to either a JSON or YML file containing a valid model, or a dictionary
        containing a model
    @raises FileNotFoundError if a string is provided that does not lead to a file
    @raises Exception if a string given does not end in .yml, .yaml, or .json
    @return a dictionary of the parsed model, with keys "variables", "outcomes", "tables", "graph", "latent"
    """

    # str: path to a file
    if isinstance(file, str):
        if not path.isfile(file):
            print(f"ERROR: Can't find {file}")
            raise FileNotFoundError

        if file.lower().endswith(".yml") or file.lower().endswith(".yaml"):
            loader = yaml_load

        elif file.lower().endswith(".json"):
            loader = json_load

        else:
            print(f"Unknown extension for file: {file}, needs to end with .yml, .yaml, or .json")
            raise FileNotFoundError

        with open(file) as f:
            data = loader(f)

    # dict: assume valid model
    else:
        data = file

    """
    variables: maps string name to the Variable object instantiated
    outcomes: maps string name *and* corresponding Variable to a list of outcome values
    tables: maps strings/Variables to corresponding ConditionalProbabilityTables
    """
    variables = dict()
    outcomes = dict()
    tables = dict()

    # set of latent variables
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
