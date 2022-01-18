from json import load as json_load
from pathlib import Path
from typing import Collection, Mapping
from loguru import logger
from yaml import safe_load as yaml_load

from .ConditionalProbabilityTable import ConditionalProbabilityTable
from .Exceptions import MissingVariable
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

    def all_variables(self) -> Collection[Variable]:
        return self._v.values()


def from_dict(data: dict) -> Model:
    return parse_model(data)


def from_path(p: Path) -> Model:
    if not p.exists() or not p.is_file():
        raise FileNotFoundError

    if p.suffix == ".json":
        return parse_model(json_load(p.read_text()))

    elif p.suffix in [".yml", ".yaml"]:
        return parse_model(yaml_load(p.read_text()))

    else:
        raise Exception(f"Unknown extension for {p}")

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

    if "exogenous" in data:
        for variable, children in data["exogenous"].items():
            v.add(variable)
            for c in children:
                v.add(c)
                e.add((variable, c))

    graph = Graph(v, e)

    return Model(graph, variables, tables)
