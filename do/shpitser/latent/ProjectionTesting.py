#!/usr/bin/env python

#########################################################
#                                                       #
#   ProjectionTesting                                   #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

from src.probability.shpitser.latent.LatentProjection import latent_projection
from src.probability.structures.Graph import Graph

# A runnable file to test the LatentGraph data structure

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
    u = graph["u"]

    # Parse minimal graph
    for line in graph["e"]:
        s = [i.strip() for i in line.split("->")]
        v.update(s)
        for i in range(len(s)-1):
            e.add((s[i], s[i+1]))

    g = Graph(v, e)

    print("\n" + "*" * 50 + "\n")
    print("Original:\n" + str(g), "\n")

    latent = latent_projection(g, u)

    print("Latent Projection:\n" + str(latent))

    print("C Components: ")
    seen = set()

    for n in latent.v:
        component = ", ".join(list(latent.c_components[n]))
        if component not in seen:
            seen.add(component)
            print(component)
