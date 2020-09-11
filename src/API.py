import itertools
import os
import webview


class API:
    """
    A Python API for pywebview, enabling the front-end JS/TS to interact with the Python backend
    """

    def __init__(self):

        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        from probability_structures.BackdoorController import BackdoorController
        from probability_structures.CausalGraph import CausalGraph
        from config.config_manager import access
        from util.ProbabilityExceptions import ProbabilityIndeterminableException
        from util.parsers.GraphLoader import parse_graph_file_data, parse_outcomes_and_interventions
        from util.helpers.PowerSet import power_set

        self._parsed = None
        self._variables = None
        self._outcomes = None
        self._tables = None
        self._graph = None
        self._cg = None
        self._bc = None


    def loaded(self):
        return True

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

        self._parsed = parse_graph_file_data(PREFIX + self.access("graph_file_folder") + "/" + graph_file)

        # Unpack the main contents of the parsed file for easier access
        self._variables = self._parsed["variables"]
        self._outcomes = self._parsed["outcomes"]
        self._tables = self._parsed["tables"]
        self._graph = self._parsed["graph"]
        self._cg = CausalGraph(**self._parsed)
        self._bc = BackdoorController(self._graph)

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

        result = self._cg.probability_query(head, body)
        if result is None:
            raise ProbabilityIndeterminableException
        return result

    def v_to_parents_and_children(self):
        s = []
        for v in sorted(self._variables):
            s.append([v, sorted(list(self._graph.parents(v))), sorted(list(self._graph.children(v)))])
        return s

    def backdoor_paths(self, x, y, z):
        self._bc: BackdoorController

        paths = []
        for cross in list(itertools.product(x, y)):
            backdoor_paths = self._bc.backdoor_paths(*cross, z)

            for path in backdoor_paths:
                msg = "  "
                for index in range(len(path) - 1):
                    msg += path[index] + " "
                    msg += " <- " if path[index] in self._graph.children(path[index + 1]) else " -> "
                paths.append(msg + path[-1])

        return paths

    def all_z_results(self, x, y):

        self._bc: BackdoorController

        results = self._bc.get_all_z_subsets(set(x), set(y))
        print(results)

        return [list(s) for s in results]

        # TODO - Would be nicer if the invalid Z sets also were returned with what paths appear

        responses = []
        for s in power_set(self._graph.v - (set(x) | set(y))):

            z = set([self._cg.variables[v] for v in s])

            response = {
                "sufficient": True,
                "paths": [],
                "z": sorted(s)
            }

            for cross in list(itertools.product(x, y)):
                x_v, x_y = self._cg.variables[cross[0]], self._cg.variables[cross[1]]

                paths = self._bc.backdoor_paths(x_v, x_y, z)
                if len(paths) > 0:
                    response["sufficient"] = False
                else:
                    print(paths)
                response["paths"] = paths

            responses.append(response)

        return responses

    def give_exception(self):
        raise Exception