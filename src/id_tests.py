from ID_algorithm import ExtendedGraph

dataset = [
    {
        "u": {"Z0", "B"},
        "e": ["Z0 -> X -> Y", "Z0 -> Z1 -> Z2 -> Y", "Z0 -> B -> Z3 -> Y", "X -> Z2 -> Z3"]
    },
    {
        "u": {"U1", "U2"},
        "e": ["U1 -> Z", "U1 -> X -> Z", "U1 -> U2 -> X", "U2 -> Z", "U2 -> Y -> Z"]
    },
    {
        "u": {"U"},
        "e": ["U -> X -> Y -> Z", "U -> Y", "U -> Z"]
    },
    {
        "u": {"U"},
        "e": ["U -> X -> W", "U -> Y -> W", "U -> Z -> Y", "X -> Y"]
    },
    {
        "u": {"U1", "U2", "U3", "U4", "U5"},
        "e": ["U1 -> U2 -> U5 -> X -> Y", "U1 -> U3 -> U4", "U2 -> U4", "U3 -> U5 -> Y"]
    }
]

for graph in dataset:

    v = set()
    e = set()

    for line in graph["e"]:
        s = [i.strip() for i in line.split("->")]
        v.update(s)
        for i in range(len(s)-1):
            e.add((s[i], s[i+1]))

    g = ExtendedGraph(v, e, graph["u"])
    print("\n\n\n\n\n**********")
    print(str(g))
    transform = g.latent_projection()
    print("\nTransform\n", str(transform))
