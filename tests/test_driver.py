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


def print_test_result(success: bool, msg: str):
    """
    Print a test result to standard out, with a header marking the success of the test
    @param success: bool; True if the test was successful, False otherwise
    @param msg: string; Any arbitrary message returned by the test
    """
    green = '\033[92m'
    fail = '\033[91m'
    end = '\033[0m'

    color = green if success else fail
    print(f"[{color}{'OK' if success else 'ERROR'}{end}]: {msg}")
