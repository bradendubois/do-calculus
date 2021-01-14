#!/usr/bin/env python

from sys import argv
from os import path, listdir
from json import dump

from graph_generator import generate_graph
from distribution_generation import generate_distribution
from probability.structures.CausalGraph import CausalGraph
from tests.RegressionTesting import basic_validation
from util.parsers.GraphLoader import parse_graph_file_data

# Default number of graphs to create
N = 10

if len(argv) != 3:
    print(len(argv), argv)
    exit()

try:
    N = int(argv[1])

except ValueError:
    print("Could not convert", argv[1], "to int; defaulting to", N)

destination_directory = argv[2]

if not path.isdir(destination_directory):
    print("Cannot resolve", destination_directory)
    exit()

while N:

    try:
        g = generate_graph()
        distribution = generate_distribution(g)

        cg = CausalGraph(**parse_graph_file_data({"variables": list(distribution.values())}))

        success, message = basic_validation(cg, "N/A")
        if success:
            l = len(listdir(destination_directory)) + 1

            with open("{}/m{}.json".format(destination_directory, l), "w") as f:
                dump({
                    "name": "m" + str(l),
                    "variables": list(distribution.values())
                }, f, indent=4, sort_keys=True)

        N -= 1

        if N:
            print(N, "graphs remaining to generate.")

    except Exception as e:
        print(e)
        continue
