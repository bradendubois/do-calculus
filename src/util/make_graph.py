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

variables = set()
parents = dict()

for edge in original_edges:
    p, c = [item.strip() for item in edge.split("->")]
    if p not in variables:
        variables.add(p)
        parents[p] = set()

    if c not in variables:
        variables.add(c)
        parents[c] = set()

    parents[c].add(p)

# TODO
