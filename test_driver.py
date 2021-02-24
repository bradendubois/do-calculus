
# api
from src.api.backdoor_paths import api_backdoor_paths, api_backdoor_paths_parse
from src.api.deconfounding_sets import api_deconfounding_sets, api_deconfounding_sets_parse
from src.api.joint_distribution_table import api_joint_distribution_table
from src.api.probability_query import api_probability_query, api_probability_query_parse

from src.probability.structures.CausalGraph import CausalGraph
from src.probability.structures.ConditionalProbabilityTable import ConditionalProbabilityTable
from src.probability.structures.Graph import Graph, to_label
from src.probability.structures.VariableStructures import Outcome, Variable, Intervention

from src.util.helpers import power_set, disjoint, minimal_sets
from src.util.ModelLoader import parse_model

from src.validation.backdoors.backdoor_path_tests import backdoor_tests
from src.validation.inference.inference_tests import inference_tests, MissingTableRow
from src.validation.shpitser.shpitser_tests import shpitser_tests

from src.validation.test_util import print_test_result

# TODO - use pathlib
graph_location = "src/graphs/full"
generated_location = "src/graphs/generated"
default_model_file = "pearl-3.4.yml"

# api

def test_api_backdoor_paths():
    ...


def test_api_deconfounding_sets():
    ...


def test_api_joint_distribution_table():
    ...


def test_api_probability_query():
    ...


# config - TODO


# graphs

def test_sum_to():
    ...


def test_generate_distribution():
    ...


def test_cycle():
    ...


def test_longest():
    ...


def test_generate_graph():
    ...


def test_randomized_latent_variables():
    ...

# TODO make model_generator into runnable function

# probability/

# probability/do_calculus - TODO

# probability/shpitser - TODO

# probability/structures

# probability/structures/BackdoorController

# see: validation


# probability/structures/CausalGraph

cg = CausalGraph(**parse_model(f"{graph_location}/{default_model_file}"))


# See: validation

# probability/structures/ConditionalProbabilityTable

def test_probability_lookup():
    t: ConditionalProbabilityTable = cg.tables["Xj"]

    priors = [Outcome("X6", "x6"), Outcome("X4", "x4"), Outcome("X5", "x5")]

    assert t.probability_lookup(Outcome("Xj", "xj"), priors) == 0.0
    assert t.probability_lookup(Outcome("Xj", "~xj"), priors) == 1.0

    try:
        assert t.probability_lookup(Outcome("Xj", "foo"), priors) == 100
        raise Exception
    except MissingTableRow:
        pass


# probability/structures/Graph

graph = cg.graph


def test_roots():
    assert sum(map(lambda v: len(graph.parents(v)), graph.roots())) == 0


def test_parents():
    graph.reset_disabled()
    roots = graph.roots()
    for vertex in graph.v:
        parents = graph.parents(vertex)
        for parent in parents:
            assert (parent, vertex) in graph.e

        if vertex in roots:
            assert len(parents) == 0
        else:
            assert len(parents) > 0


def test_children():
    graph.reset_disabled()
    for vertex in graph.v:
        children = graph.children(vertex)
        for child in children:
            assert (vertex, child) in graph.e

        for child in children:
            assert vertex in graph.parents(child)


def test_ancestors():
    graph.reset_disabled()
    for vertex in graph.v:
        ancestors = graph.ancestors(vertex)
        for ancestor in ancestors:
            assert vertex in graph.reach(ancestor)


def test_reach():
    graph.reset_disabled()
    for vertex in graph.v:
        descendants = graph.reach(vertex)
        for descendant in descendants:
            assert vertex in graph.ancestors(descendant)


def test_disable_outgoing():

    graph.reset_disabled()

    for v in graph.v:
        children = graph.children(v)
        descendants = graph.reach(v)
        graph.disable_outgoing(v)
        assert len(graph.children(v)) == 0
        assert len(graph.reach(v)) == 0
        for child in children:
            assert v not in graph.parents(child)
        for descendant in descendants:
            assert v not in graph.ancestors(descendant)

    graph.reset_disabled()


def test_disable_incoming():

    graph.reset_disabled()

    for v in graph.v:
        parents = graph.parents(v)
        ancestors = graph.ancestors(v)
        graph.disable_incoming(v)
        assert len(graph.parents(v)) == 0
        assert len(graph.ancestors(v)) == 0
        for parent in parents:
            assert v not in graph.children(parent)
        for ancestor in ancestors:
            assert v not in graph.reach(ancestor)

    graph.reset_disabled()


def test_reset_disabled():
    ...


def test_get_topology():
    ...


def test_graph_copy():
    graph_2 = graph.copy()

    assert len(graph.v) == len(graph_2.v)
    assert len(graph.e) == len(graph_2.e)

    assert graph.v is not graph_2.v
    assert graph.e is not graph_2.e

    for v in graph.v:
        assert v in graph_2.v

    for v in graph_2.v:
        assert v in graph.v

    for e in graph.e:
        assert e in graph_2.e

    for e in graph_2.e:
        assert e in graph.e


def test_topological_variable_sort():
    ...


def test_descendant_first_sort():
    ...


def test_to_label():
    outcome = Outcome("Xj", "xj")
    intervention = Intervention("Xj", "xj")
    variable = Variable("Xj", [], [])

    assert to_label(outcome) == outcome.name
    assert to_label(intervention) == intervention.name
    assert to_label(variable) == variable.name


# probability/structures/Probability_Engine

def test_probability():
    ...


# probability/structures/VariableStructures

def test_outcome():
    o1 = Outcome("X", "x")
    o2 = Outcome("X", "~x")
    o3 = Outcome("Y", "y")

    assert o1 != o2
    assert o1 == "X"
    assert o1 != o2 and o2 != o3

    o1_copy = o1.copy()

    assert o1 == o1_copy and o1 is not o1_copy


def test_variable():
    ...


def test_intervention():
    t1 = Intervention("X", "x")
    t2 = Intervention("X", "~x")
    t3 = Intervention("Y", "y")

    assert t1 != t2
    assert t1 == "X"
    assert t1 != t2 and t2 != t3

    t1_copy = t1.copy()

    assert t1 == t1_copy and t1 is not t1_copy


def test_parse_outcomes_and_interventions():
    ...


# util/

def test_power_set():
    data = [1, 2, 3, 4]
    with_empty = power_set(data, allow_empty_set=True)
    without_empty = power_set(data, allow_empty_set=False)
    assert len(set(with_empty)) == 2 ** len(data)
    assert len(set(without_empty)) == 2 ** len(data) - 1


def test_minimal_sets():
    s1 = {1, 2, 3}
    s2 = {1, 2, 3, 4}
    s3 = {0, 1, 2, 3, 4}
    s4 = {5, 6, 7}
    s5 = {0, 1, 2, 3, 4, 5, 6, 7}

    minimums = minimal_sets(s1, s2, s3, s4, s5)
    assert minimums == [s1, s4]

    assert minimal_sets(s1) == [s1]
    assert minimal_sets(s1, s2) == [s1]
    assert minimal_sets(s1, s4) == [s1, s4]


def test_disjoint():
    d1 = {0, 1, 2, 3, 4}
    d2 = {3, 4, 5, 6, 7}
    d3 = {6, 7, 8, 9, 10}
    assert not disjoint(d1, d2)
    assert not disjoint(d2, d3)
    assert not disjoint(d1, d2, d3)
    assert disjoint(d1, d3)


def test_parse_model():

    # nonexistent file
    try:
        parse_model("fake/path/fake")
        raise Exception
    except FileNotFoundError:
        pass

    # invalid file
    try:
        parse_model("src/util/helpers.py")
        raise Exception
    except FileNotFoundError:
        pass

    # yml
    parse_model(f"{graph_location}/{default_model_file}")

    # json


# validation

def test_inference_module() -> bool:
    inference_bool, inference_msg = inference_tests(graph_location)
    assert inference_bool, inference_msg
    print_test_result(inference_bool, inference_msg)
    return inference_bool


def test_backdoor_module() -> bool:
    backdoor_bool, backdoor_msg = backdoor_tests(graph_location)
    assert backdoor_bool, backdoor_msg
    print_test_result(backdoor_bool, backdoor_msg)
    return backdoor_bool


def test_shpitser_module() -> bool:
    shpitser_bool, shpitser_msg = shpitser_tests(graph_location)
    assert shpitser_bool, shpitser_msg
    print_test_result(shpitser_bool, shpitser_msg)
    return shpitser_bool
