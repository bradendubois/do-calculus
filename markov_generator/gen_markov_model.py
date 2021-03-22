#!/usr/bin/env python

from json import dump
from pathlib import Path
from random import randrange
from sys import argv

from do.structures.CausalGraph import CausalGraph
from do.util.ModelLoader import parse_model

from tests.inference.inference_tests import model_inference_validation

from .gen_graph import generate_graph, randomized_latent_variables
from .gen_distribution import generate_distribution

# Default number of graphs to create
N = 10

if len(argv) != 3:
    print(len(argv), argv)
    exit()

try:
    N = int(argv[1])

except ValueError:
    print("Could not convert", argv[1], "to int; defaulting to", N)

destination_directory = Path("", argv[2])

if not destination_directory.is_dir():
    print("Cannot resolve", destination_directory)
    exit()

while N:

    try:

        num_vertices = randrange(5, 15)
        max_path_length = randrange(round(.2 * num_vertices), round(.8 * num_vertices))
        num_edges = randrange(num_vertices - 1, round(3 * num_vertices))

        g = generate_graph(num_vertices, max_path_length, num_edges)
        distribution = generate_distribution(g)

        cg = CausalGraph(**parse_model({"model": list(distribution.values())}))

        success, message = model_inference_validation(cg)
        if success:

            l = len(list(destination_directory.iterdir())) // 2 + 1

            with (destination_directory / f"m{l}").open("w") as f:
                dump({
                    "name": "m" + str(l),
                    "variables": list(distribution.values()),
                    "latent-model": False
                }, f, indent=4, sort_keys=True)

            latent_variables = randomized_latent_variables(g)
            for v in latent_variables:
                distribution[v]["latent"] = True

            with (destination_directory / f"m{l}_L").open("w") as f:
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
