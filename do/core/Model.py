from json import load as json_load
from pathlib import Path
from typing import Mapping, Union
from yaml import safe_load as yaml_load

from .ConditionalProbabilityTable import ConditionalProbabilityTable
from .Graph import Graph
from .Variables import Variable

class Model:

    def __init__(self, graph: Graph, variables: Mapping[str, Variable], distribution: Mapping[Variable, ConditionalProbabilityTable]):
        ...

class CausalGraph:
    """Handles probability queries / joint distributions on the given Causal Graph"""

    def __init__(self, graph: Graph, variables: dict, outcomes: dict, tables: dict, latent: set, **kwargs):
        """
        Initialize a Causal Graph to compute standard probability queries as well as interventional, as per the
        do-calculus of Judea Pearl, with deconfounding sets handled automatically.
        @param graph: A Graph object representing a given model
        @param variables: A dictionary mapping a string name of a variable to a Variable object
        @param outcomes: A dictionary mapping both a string name of a Variable, as well as the Variable object itself
            to a list of possible outcome values for the variable.
        @param tables: A dictionary mapping both a string name of a Variable, as well as the Variable object itself to
            a given ConditionalProbabilityTable object.
        @param latent: A set of variables, both string name as well as the Variable object itself, representing all
            latent (unobservable) variables in the given model.
        @param kwargs: Any arbitrary additional keyword arguments, allowing a model loaded using a library to be
            unpacked into an initializer call using the ** prefix.
        """
        self.graph = graph.copy()
        self.variables = variables.copy()
        self.outcomes = outcomes.copy()
        self.tables = tables.copy()
        self.latent = latent.copy()


def parse_model(file: Union[dict, str, Path]):
    """
    Parse a given model for use within the project, such as to create a CausalGraph
    @param file: a string path to either a JSON or YML file containing a valid model, or a dictionary
        containing a model
    @raise FileNotFoundError if a string is provided that does not lead to a file
    @raise Exception if a string given does not end in .yml, .yaml, or .json
    @return a dictionary of the parsed model, with keys "variables", "outcomes", "tables", "graph", "latent"
    """

    # str: path to a file, or Path
    if not isinstance(file, dict):

        if isinstance(file, Path):
            p = file

        else:
            p = Path(file)

        if not p.is_file():
            print(f"ERROR: Can't find {file}")
            raise FileNotFoundError

        extension = p.suffix.lower()

        if extension in [".yml", ".yaml"]:
            loader = yaml_load

        elif extension == ".json":
            loader = json_load

        else:
            print(f"Unknown extension '{extension}' for file: {file}, needs to end with .yml, .yaml, or .json")
            raise FileNotFoundError

        with p.open("r") as f:
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

        if "table" not in detail:
            latent.add(name)
            latent.add(variable)

        else:
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
