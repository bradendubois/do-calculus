from random import choices, randint

from do.structures.VariableStructures import Variable, Outcome, Intervention
from do.structures.Graph import Graph, to_label

from ..test_driver import graph


# do/structures/Graph

def test_roots():
    assert sum(map(lambda v: len(graph.parents(v)), graph.roots())) == 0


def test_descendants():
    assert sum(map(lambda v: len(graph.children(v)), graph.sinks())) == 0


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
            assert vertex in graph.descendants(ancestor)


def test_reach():
    graph.reset_disabled()
    for vertex in graph.v:
        descendants = graph.descendants(vertex)
        for descendant in descendants:
            assert vertex in graph.ancestors(descendant)


def test_disable_outgoing():

    graph.reset_disabled()

    for v in graph.v:
        children = graph.children(v)
        descendants = graph.descendants(v)
        graph.disable_outgoing(v)
        assert len(graph.children(v)) == 0
        assert len(graph.descendants(v)) == 0
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
            assert v not in graph.descendants(ancestor)

    graph.reset_disabled()


def test_reset_disabled():

    graph.reset_disabled()

    assert len(graph.incoming_disabled) == 0 and len(graph.outgoing_disabled) == 0

    graph.disable_incoming(*list(choices(list(graph.v), k=randint(1, len(graph.v) - 1))))
    graph.disable_outgoing(*list(choices(list(graph.v), k=randint(1, len(graph.v) - 1))))

    assert len(graph.incoming_disabled) != 0 and len(graph.outgoing_disabled) != 0

    graph.reset_disabled()

    assert len(graph.incoming_disabled) == 0 and len(graph.outgoing_disabled) == 0


def test_topology_sort():

    topology = graph.topology_sort()

    print(topology)

    for i, v in enumerate(topology):
        for before in topology[:i]:
            assert before not in graph.descendants(v)

        for after in topology[i:]:
            assert after not in graph.ancestors(v)


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


def test_without_incoming_edges():

    g = graph.copy()

    roots = g.roots()
    root_children = set().union(*[g.children(x) for x in roots])

    nop = g.without_incoming_edges(roots)       # roots have no incoming; should change nothing
    op = g.without_incoming_edges(root_children)     # sever initial roots

    assert g.v == nop.v and g.e == nop.e    # ensure no change

    assert g.v == op.v
    assert g.e != op.e
    assert len(g.e) > len(op.e)
    assert len(op.roots()) > len(g.roots())
    assert op.roots() == set(g.roots()) | root_children


def test_without_outgoing_edges():

    g: Graph = graph.copy()

    sinks = g.sinks()
    sink_parents = set().union(*[g.parents(x) for x in sinks])

    nop = g.without_outgoing_edges(sinks)       # sinks have no outgoing; should change nothing
    op = g.without_outgoing_edges(sink_parents)     # sever initial sinks

    assert g.v == nop.v and g.e == nop.e    # ensure no change

    assert g.v == op.v
    assert g.e != op.e
    assert len(g.e) > len(op.e)
    assert len(op.sinks()) > len(g.sinks())
    assert op.sinks() == set(g.sinks()) | sink_parents


def test_to_label():
    outcome = Outcome("Xj", "xj")
    intervention = Intervention("Xj", "xj")
    variable = Variable("Xj", [], [])

    assert to_label(outcome) == outcome.name
    assert to_label(intervention) == intervention.name
    assert to_label(variable) == variable.name
