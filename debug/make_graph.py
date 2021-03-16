
"""
original_edges = [
    "Z0 -> X",
    "X -> Y",
    "Z0 -> Z1",
    "Z1 -> Z2",
    "Z2 -> Y",
    "Z0 -> B",
    "B -> Z3",
    "Z3 -> Y",
    "X -> Z2",
    "Z2 -> Z3"
]
"""


def create_graph(edge_strings: list) -> (set, set):
    """
    Create a graph from a list of edges
    @param edge_strings: A list of strings, where each string is of the form "X -> Y"
    @return: Two sets, V and E, used to construct a graph.
    """

    v = set()
    e = set()

    for edge in edge_strings:
        s, t = [item.strip() for item in edge.split("->")]
        if s not in v:
            v.add(s)

        if t not in v:
            v.add(t)

        e.add((s, t))

    return v, e
