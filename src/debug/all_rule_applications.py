
from probability_structures.do_calculus.application.rules.DoCalculusRules import *
from probability_structures.Graph import Graph
from util.helpers.PowerSet import power_set

from sys import argv
from os import path

if len(argv) == 1:
    print("No graph specified.")
    exit(0)

filename = argv[1]

if not path.isfile(filename):
    print("The specified filename either does not exist, or is not a file.")
    exit(0)

v = set()
e = set()

# These graphs should look like:
# x->y->z
# z -> w

with open(filename) as f:
    for line in f:
        s = [i.strip() for i in line.split("->")]
        v.update(s)
        for i in range(len(s)-1):
            e.add((s[i], s[i+1]))

g = Graph(v, e)

applies = []

for y in power_set(v, False):

    l_y = set(v) - set(y)
    for x in power_set(l_y, True):

        l_x = set(l_y) - set(x)
        for z in power_set(l_x, True):

            l_z = set(l_x) - set(z)
            for w in power_set(l_z, True):

                r1 = rule_1_applicable(g, y, x, z, w)
                r2 = rule_2_applicable(g, y, x, z, w)
                r3 = rule_3_applicable(g, y, x, z, w)

                applies.append((y, x, z, w, str(r1), str(r2), str(r3)))

print("| Y | X | Z | W | Rule 1 | Rule 2 | Rule 3 |")
print("| :-: | :-: | :-: | :-: | :-: | :-: | :-: |")

for s in applies:

    print("|", end="")
    for item in s:
        print(" ", end="")
        if isinstance(item, tuple) and len(item) == 0:
            print("{}", end="")
        elif isinstance(item, tuple):
            print(", ".join(sorted(item)), end="")
        else:
            print(str(item), end="")
        print(" |", end="")
    print()
