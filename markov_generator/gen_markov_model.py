#!/usr/bin/env python

from itertools import product
from json import dump
from pathlib import Path
from random import choices
from sys import argv

from do.structures.CausalGraph import CausalGraph
from do.structures.VariableStructures import Outcome
from do.util.ModelLoader import parse_model

from tests.modules.inference.inference_tests import model_inference_validation

from .gen_graph import generate_graph, randomized_latent_variables
from .gen_distribution import generate_distribution


def semi_markov_transform(model: dict, k=1):

    new_model = {k: v.copy() for k, v in model.items()}

    cg = CausalGraph(**parse_model(new_model))
    graph = cg.graph

    roots = choices(list(graph.roots()), k=k)
    root_children = set().union(*[graph.children(v) for v in roots])

    for child in root_children:

        observable_parents = sorted(list(graph.parents(child) - set(roots)))

        new_distribution = []

        for outcome in cg.outcomes[child]:
            for cross in product(*[cg.outcomes[p] for p in observable_parents]):
                outcomes = {Outcome(x, cross[i]) for i, x in enumerate(observable_parents)}
                new_distribution.append([outcome, *cross, cg.probability_query({Outcome(child, outcome)}, outcomes)])

        new_model["model"][child]["table"] = new_distribution
        new_model["model"][child]["parents"] = observable_parents + list(set(graph.parents(child)) - set(observable_parents))

    for root in roots:
        new_model["model"].pop(root)

    return new_model


def markov_model(num_vertices, max_path_length, num_edges) -> dict:

    g = generate_graph(num_vertices, max_path_length, num_edges)
    model = {
        "model": generate_distribution(g)
    }

    print("Dist", model)
    cg = CausalGraph(**parse_model(model))

    success, message = model_inference_validation(cg)
    assert success, message

    return model


def create_k_models(n, destination_directory, k, num_vertices=10, max_length=10, num_edges=10):

    destination = Path(destination_directory)

    to_generate = n

    markov_directory = destination / "markov"
    semi_markov_directory = destination / "semi_markov"

    for path in [destination, markov_directory, semi_markov_directory]:

        if not path.exists():
            path.mkdir()

        elif path.is_file():
            print(f"{path} already exists!")
            exit()

    generated = 0

    while to_generate:

        try:

            generated_model = markov_model(num_vertices, max_length, num_edges)

            model_number = len(list(markov_directory.iterdir())) + 1

            with (markov_directory / f"m{model_number}.json").open("w") as f:
                dump({
                    "name": "m" + str(model_number),
                    "model": generated_model
                }, f, indent=4, sort_keys=True)

            semi_markov = semi_markov_transform(generated_model, k=k)

            with (semi_markov_directory / f"m{model_number}.json").open("w") as f:
                dump({
                    "name": "m" + str(model_number) + "_L",
                    "model": semi_markov,
                }, f, indent=4, sort_keys=True)

            generated += 1

        except AssertionError:
            print("Failed run.")

        to_generate -= 1

    return generated


if __name__ == "__main__":

    if len(argv) != 4:
        print(f"Expected 4 arguments, got {len(argv)}!")
        print(f"python gen_markov_model num_models destination_directory latent_roots")
        exit()

    generate = 1
    latent_roots = 1
    try:
        generate = int(argv[1])
        latent_roots = int(argv[3])

    except ValueError:
        print(f"Could not convert {argv[1]} or {argv[3]} to int")
        exit()

    while generate:
        generate -= create_k_models(generate, argv[2], latent_roots)
