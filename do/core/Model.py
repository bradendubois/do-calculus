from json import load as json_load
from pathlib import Path
from typing import Mapping
from loguru import logger
from yaml import safe_load as yaml_load

from do.core.Exceptions import MissingVariable

from .ConditionalProbabilityTable import ConditionalProbabilityTable
from .Graph import Graph
from .Variables import Variable

class Model:

    def __init__(self, graph: Graph, variables: Mapping[str, Variable], distribution: Mapping[Variable, ConditionalProbabilityTable]):
        self._g = graph.copy()
        self._v = {k: variables[k] for k in variables}
        self._d = {k: distribution[k] for k in distribution}

    def graph(self) -> Graph:
        return self._g

    def variable(self, key: str) -> Variable:
        if key not in self._v:
            logger.error(f"unknown variable: {key}")
            raise MissingVariable(key)
        return self._v[key]

    def table(self, key: str) -> ConditionalProbabilityTable:
        if key not in self._v:
            logger.error(f"unknown variable: {key}")
            raise MissingVariable(key)
        return self._d[key]


def validate(model: Model) -> bool:
    """
    Ensures a model is 'valid' and 'consistent'.
    1. Ensures the is a DAG (contains no cycles)
    2. Ensures all variables denoted as exogenous lack a table and are roots.
    3. Ensures all variables denoted as endogenous contain a table.
    4. Ensures all distributions are consistent (the sum of probability of each outcome is 1.0)

    Returns True on success (indicating a valid model), or raises an appropriate Exception indicating a failure.
    """
    ...


def from_json(path: str) -> Model:
    with Path(path).open() as f:
        data = json_load(f)
    return parse_model(data)


def from_yaml(path: str) -> Model:
    with Path(path).open() as f:
        data = yaml_load(f)
    return parse_model(data)


def from_dict(data: dict) -> Model:
    return parse_model(data)


def parse_model(data: dict) -> Model:

    """
    variables: maps string name to the Variable object instantiated
    outcomes: maps string name *and* corresponding Variable to a list of outcome values
    tables: maps strings/Variables to corresponding ConditionalProbabilityTables
    """
    variables = dict()
    outcomes = dict()
    tables = dict()

    for name, detail in data["endogenous"].items():

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

    for variable, children in data["exogenous"].items():
        v.add(variable)
        for c in children:
            v.add(c)
            e.add((variable, c))

    graph = Graph(v, e)

    return Model(graph, variables, tables)
