import webview
import os

from python.probability_structures.CausalGraph import CausalGraph
from python.config.config_manager import access
from python.util.parsers.GraphLoader import parse_graph_file_data, parse_outcomes_and_interventions

# Maybe this has to change for a build? How to get the path in dev, as well as a build?
PREFIX = "src/python/"


class API:
    """
    A Python API for pywebview, enabling the front-end JS/TS to interact with the Python backend
    """

    def __init__(self):

        self.parsed = None
        self._variables = None
        self._outcomes = None
        self._tables = None
        self._graph = None
        self._cg = None

    def fullscreen(self):
        webview.windows[0].toggle_fullscreen()

    def save_content(self, content):
        filename = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG)
        if not filename:
            return

        with open(filename, 'w') as f:
            f.write(content)

    def access(self, param):
        return access(param)

    def get_graph_names(self):
        return sorted([f for f in os.listdir(PREFIX + self.access("graph_file_folder")) if f.endswith(".json")])

    def all_variable_data(self):
        return [[i, self._variables[i].outcomes, self._variables[i].parents] for i in sorted(self._variables)]

    def variable_table(self, v: str):
        t = self._tables[v]
        return [[v, t.given, "P"], *[[row[0].outcome, [x.outcome for x in row[1]], row[2]] for row in t.table_rows]]

    def load_file(self, graph_file):

        self.parsed = parse_graph_file_data(PREFIX + self.access("graph_file_folder") + "/" + graph_file)

        # Unpack the main contents of the parsed file for easier access
        self._variables = self.parsed["variables"]
        self._outcomes = self.parsed["outcomes"]
        self._tables = self.parsed["tables"]
        self._graph = self.parsed["graph"]
        self._cg = CausalGraph(**self.parsed)

        return True

    def variables(self):
        return sorted([k for k in self._variables])

    def outcomes(self, variable):
        return self._outcomes[variable]

    def outcome_dict(self):
        return {k: self._outcomes[k] for k in self._variables}

    def execute_query(self, query: str):

        if "|" in query:
            s = query.split("|")
            head, body = parse_outcomes_and_interventions(s[0]), parse_outcomes_and_interventions(s[1])
        else:
            head, body = parse_outcomes_and_interventions(query), []

        return self._cg.probability_query(head, body)
