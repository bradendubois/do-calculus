from math import prod
from pathlib import Path

# api
from do.api.backdoor_paths import api_backdoor_paths, api_backdoor_paths_parse
from do.api.deconfounding_sets import api_deconfounding_sets, api_deconfounding_sets_parse
from do.api.joint_distribution_table import api_joint_distribution_table
from do.api.probability_query import api_probability_query, api_probability_query_parse

from do.structures.BackdoorController import BackdoorController
from do.structures.CausalGraph import CausalGraph
from do.structures.ConditionalProbabilityTable import ConditionalProbabilityTable
from do.structures.Graph import Graph, to_label
from do.structures.VariableStructures import Outcome, Variable, Intervention

from do.util.helpers import power_set, disjoint, minimal_sets, within_precision
from do.util.ModelLoader import parse_model

from tests.backdoors.backdoor_path_tests import backdoor_tests
from tests.inference.inference_tests import inference_tests, MissingTableRow
from tests.shpitser.shpitser_tests import shpitser_tests

from tests.test_util import print_test_result


# Use the Xi-Xj model of TBoW as a test
default_model_file = "pearl-3.4.yml"

# Default location for the graphs made by hand
graphs = Path("do", "graphs")

# Path to the Xi-Xj model
test_file = graphs / default_model_file


cg = CausalGraph(**parse_model(test_file))
graph = cg.graph
bc = BackdoorController(graph)

json_model = graphs / "test.json"


# api

def test_api_backdoor_paths():

    blocked = ({"Xi"}, {"Xj"}, {"X4", "X2"})
    unblocked = ({"Xi"}, {"Xj"}, set())

    assert api_backdoor_paths_parse("Xi -> Xj") == {"src": {"Xi"}, "dst": {"Xj"}, "dcf": set()}
    assert api_backdoor_paths_parse("Xi -> Xj | X4, X2") == {"src": {"Xi"}, "dst": {"Xj"}, "dcf": {"X4", "X2"}}

    assert len(api_backdoor_paths(bc, *unblocked)) > 0
    assert len(api_backdoor_paths(bc, *blocked)) == 0

    assert api_backdoor_paths(bc, *unblocked) == bc.backdoor_paths(*unblocked)
    assert api_backdoor_paths(bc, *blocked) == bc.backdoor_paths(*blocked)


def test_api_deconfounding_sets():

    paths = ({"Xi"}, {"Xj"})
    paths2 = ({"Xj"}, {"Xi"})
    no_paths = ({"X1"}, {"Xj"})

    unfixable = ({"Xi", "X4", "X2"}, {"Xj"})

    assert api_deconfounding_sets_parse("Xi, X1 -> Xj") == {"src": {"Xi", "X1"}, "dst": {"Xj"}}
    assert api_deconfounding_sets_parse("Xi -> Xj") == {"src": {"Xi"}, "dst": {"Xj"}}
    assert api_deconfounding_sets_parse("Xj -> Xi") == {"src": {"Xj"}, "dst": {"Xi"}}
    assert api_deconfounding_sets_parse("X1 -> Xj") == {"src": {"X1"}, "dst": {"Xj"}}
    assert api_deconfounding_sets_parse("Xi, X4, X2 -> Xj") == {"src": {"Xi", "X4", "X2"}, "dst": {"Xj"}}

    assert len(api_deconfounding_sets(bc, *paths)) > 0
    assert len(api_deconfounding_sets(bc, *paths2)) > 0
    assert len(api_deconfounding_sets(bc, *no_paths)) > 0
    assert len(api_deconfounding_sets(bc, *unfixable)) == 0

    assert api_deconfounding_sets(bc, *paths) == bc.all_dcf_sets(*paths)
    assert api_deconfounding_sets(bc, *paths2) == bc.all_dcf_sets(*paths2)
    assert api_deconfounding_sets(bc, *no_paths) == bc.all_dcf_sets(*no_paths)
    assert api_deconfounding_sets(bc, *unfixable) == bc.all_dcf_sets(*unfixable)


def test_api_joint_distribution_table():

    jdt: ConditionalProbabilityTable = api_joint_distribution_table(cg)

    outcome_counts = list(map(lambda v: len(cg.outcomes[v]), cg.variables))
    totals = map(lambda row: row[-1], jdt.table_rows[:-1])

    assert isinstance(jdt, ConditionalProbabilityTable)
    assert len(jdt.table_rows[:-1]) == prod(outcome_counts)
    assert within_precision(sum(list(totals)), 1)


def test_api_probability_query():

    x = Outcome("X", "x")
    y = Outcome("Y", "y")
    z = Outcome("Z", "z")

    v = Intervention("V", "v")
    w = Intervention("W", "w")

    head_and_body = "Y=y, X=x | Z=z, do(W=w, V=v)"
    head_only = "Y=y, X=x"
    single_both = "Y=y | X = x"
    single_head = "Y = y"

    assert api_probability_query_parse(head_and_body) == {"y": {y, x}, "x": {z, w, v}}
    assert api_probability_query_parse(head_only) == {"y": {y, x}, "x": set()}
    assert api_probability_query_parse(single_both) == {"y": {y}, "x": {x}}
    assert api_probability_query_parse(single_head) == {"y": {y}, "x": set()}

    xi = Outcome("Xi", "xi")
    xj = Outcome("Xj", "xj")
    assert api_probability_query(cg, {xj}, {xi}) == cg.probability_query({xj}, {xi})


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


# See: validation

# probability/structures/ConditionalProbabilityTable

def test_probability_lookup():
    t: ConditionalProbabilityTable = cg.tables["Xj"]

    priors = [Outcome("X6", "x6"), Outcome("X4", "x4"), Outcome("X5", "x5")]

    assert t.probability_lookup(Outcome("Xj", "xj"), priors) == 0.0
    assert t.probability_lookup(Outcome("Xj", "~xj"), priors) == 1.0

    try:
        assert t.probability_lookup(Outcome("Xj", "foo"), priors) == 100
        raise Exception     # coverage: skip
    except MissingTableRow:
        pass


# probability/structures/Graph

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

    for v in cg.variables.values():

        v: Variable

        assert isinstance(v.name, str)
        assert isinstance(v.reach, set)
        assert isinstance(v.parents, list)
        assert isinstance(v.topological_order, int)

        c = v.copy()

        assert v == c
        assert v is not c

        assert v.name == c.name

        assert v.reach is not c.reach
        assert v.reach == c.reach

        assert v.parents is not c.parents
        assert v.parents == c.parents

        assert v.topological_order == c.topological_order

        assert hash(v) == hash(c)

        # Unique enough hashing function
        assert list(map(lambda variable: hash(variable), cg.variables.values())).count(hash(v)) <= 3
        assert str(v) == str(c)

        assert v == v.name


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
        parse_model(Path("fake", "path", "fake"))
        raise Exception     # coverage: skip
    except FileNotFoundError:
        pass

    # invalid file
    try:
        parse_model(Path("do", "util", "helpers.py"))
        raise Exception     # coverage: skip
    except FileNotFoundError:
        pass

    # string path
    parse_model(str(test_file.absolute()))

    # yml
    parse_model(test_file)

    # json
    parse_model(json_model)


# validation

def test_inference_module() -> bool:
    inference_bool, inference_msg = inference_tests(graphs)
    assert inference_bool, inference_msg
    print_test_result(inference_bool, inference_msg)
    return inference_bool


def test_backdoor_module() -> bool:
    backdoor_bool, backdoor_msg = backdoor_tests(graphs)
    assert backdoor_bool, backdoor_msg
    print_test_result(backdoor_bool, backdoor_msg)
    return backdoor_bool


def test_shpitser_module() -> bool:
    shpitser_bool, shpitser_msg = shpitser_tests(graphs)
    assert shpitser_bool, shpitser_msg
    print_test_result(shpitser_bool, shpitser_msg)
    return shpitser_bool
