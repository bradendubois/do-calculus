from os.path import dirname, abspath
from pathlib import Path
from yaml import safe_load as load

from do.shpitser.identification.IDAlgorithm import ID
from do.shpitser.identification.IDProcessing import parse_shpitser
from do.structures.CausalGraph import CausalGraph
from do.structures.Exceptions import NoDeconfoundingSet
from do.structures.VariableStructures import Outcome, Intervention
from do.util.helpers import power_set, within_precision
from do.util.ModelLoader import parse_model

from ...print_test_result import print_test_result

shpitser_test_module = Path(dirname(abspath(__file__)))

test_file_directory = shpitser_test_module / "test_files"

markov_model_directory = shpitser_test_module / "models" / "markov"
semi_markov_model_directory = shpitser_test_module / "models" / "semi_markov"


def shpitser_parity(markov_cg: CausalGraph, semi_markov_cg: CausalGraph) -> (bool, str):
    """

    @param markov_cg:
    @param semi_markov_cg:
    @return:
    """

    v = set(semi_markov_cg.variables)

    for y in power_set(v, allow_empty_set=False):

        for x in power_set(v - set(y), allow_empty_set=True):

            try:

                # Regular backdoor criteria with
                print("YO", v)
                y_outcomes = {Outcome(s, markov_cg.outcomes[s][0]) for s in y}
                x_do = [Intervention(s, markov_cg.outcomes[s][0]) for s in x]

                try:
                    markov_p = markov_cg.probability_query(y_outcomes, x_do)

                # Just indicates that the backdoor criterion cannot apply here
                except NoDeconfoundingSet:  # coverage: skip
                    continue

                shpitser_expression = ID(y, x, semi_markov_cg.graph, semi_markov_cg.tables)
                shpitser_expression_p = parse_shpitser(shpitser_expression, semi_markov_cg, {k: x_do[i] for i, k in enumerate(x)})

                print(markov_p, shpitser_expression_p)
                assert within_precision(markov_p, shpitser_expression_p)

            # Didn't match the expected total
            except AssertionError as e:     # coverage: skip
                return False, f"Failed assertion: {e}"

    return True, "Basic tests passed."


def shpitser_tests(graph_location: Path) -> (bool, str):
    """
    Run all tests related to the implementation algorithm 3 of Shpitser & Pearl, 2006.
    @param graph_location:
    @return:
    """

    markov_files = sorted(list(markov_model_directory.iterdir()))
    semi_markov_files = sorted(list(semi_markov_model_directory.iterdir()))

    assert len(markov_files) > 0 and len(semi_markov_files) > 0, "Models not found"
    assert len(markov_files) == len(semi_markov_files), "Markov and semi-Markov directories do not match sizes"

    all_successful = True

    for markov, semi_markov in zip(markov_files, semi_markov_files):

        # Load the models

        with markov.open("r") as f:
            markov_model = load(f)

        with semi_markov.open("r") as f:
            semi_markov_model = load(f)

        print(markov_model)

        print("*******")

        print(semi_markov_model)

        # Parse and create Causal Graphs

        markov_cg = CausalGraph(**parse_model(markov_model))
        semi_markov_cg = CausalGraph(**parse_model(semi_markov_model))

        # Ensure parity

        success, msg = shpitser_parity(markov_cg, semi_markov_cg)
        print_test_result(success, msg if not success else f"All tests in {markov_model.stem} v {markov_model.stem} passed")

        if not success:     # coverage: skip
            all_successful = False

    return all_successful, "Shpitser module passed" if all_successful else "Shpitser module encountered errors"
