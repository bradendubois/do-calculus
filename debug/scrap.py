from pathlib import Path
from do.structures.Graph import Graph
from yaml import safe_dump

from gen_distribution import generate_distribution

V = {"U1", "U2", "U3", "A", "B", "X", "Z", "W", "Y"}
E = {
    ("U1", "A"), ("U1", "X"),
    ("U2", "A"), ("U2", "Y"),
    ("U3", "X"), ("U3", "W"),
    ("A", "B"), ("B", "X"), ("X", "Z"), ("X", "W"), ("Z", "Y"), ("W", "Y")
}

G = Graph(V, E)

distribution = generate_distribution(G)

P = Path(".", "../shpitser2a.yml")

with P.open("w") as f:
    safe_dump({
        "name": "Shpitser Figure 2a",
        "model": distribution

    }, f)
