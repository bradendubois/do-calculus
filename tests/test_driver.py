from pathlib import Path

from do.structures.BackdoorController import BackdoorController
from do.structures.CausalGraph import CausalGraph
from do.util.ModelLoader import parse_model

graphs = Path("do", "graphs")               # Default location for the graphs made by hand

test_file = graphs / "pearl-3.4.yml"        # Use the Xi-Xj model of TBoW as a test
json_model = graphs / "test.json"

# These will be loaded / imported through other tests
cg = CausalGraph(**parse_model(test_file))
graph = cg.graph
bc = BackdoorController(graph)
