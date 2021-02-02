#!/usr/bin/env python

from sys import argv
from os import path, listdir
from json import dump
from random import randrange

from graph_generator import generate_graph, randomized_latent_variables
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

        num_vertices = randrange(5, 15)
        max_path_length = randrange(round(.2 * num_vertices), round(.8 * num_vertices))
        num_edges = randrange(num_vertices - 1, round(3 * num_vertices))

        g = generate_graph(num_vertices, max_path_length, num_edges)
        distribution = generate_distribution(g)

        cg = CausalGraph(**parse_graph_file_data({"variables": list(distribution.values())}))

        success, message = basic_validation(cg, "N/A")
        if success:

            l = len(listdir(destination_directory)) // 2 + 1

            with open("{}/m{}.json".format(destination_directory, l), "w") as f:
                dump({
                    "name": "m" + str(l),
                    "variables": list(distribution.values()),
                    "latent-model": False
                }, f, indent=4, sort_keys=True)

            latent_variables = randomized_latent_variables(g)
            for v in latent_variables:
                distribution[v]["latent"] = True

            with open("{}/m{}_L.json".format(destination_directory, l), "w") as f:
                dump({
                    "name": "m" + str(l) + "_L",
                    "variables": list(distribution.values()),
                    "latent-model": True
                }, f, indent=4, sort_keys=True)

        N -= 1

        if N:
            print()
            print(N, "graph(s) remaining to generate.")
            print()

    except AssertionError as e:
        print(e)
        continue
