from probability_structures.Graph import Graph

from sys import argv
from os import path

from probability_structures.do_calculus.DoCalculus import do_calculus_repl

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
print(str(g))

while True:

    do_calculus_repl(g, dict(), dict())

    print()
    if input("Exit? (Yes/Y): ").lower().strip() in ["yes", "y"]:
        exit(0)
