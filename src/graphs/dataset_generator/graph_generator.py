#!/usr/bin/env python

from string import ascii_uppercase

import random
import itertools

from src.probability.structures.Graph import Graph


def cycle(v, e):

    mid = set()
    end = set()

    def _cycle(cur):

        if cur in end:
            return False

        elif cur in mid:
            return True

        else:
            mid.add(cur)
            outgoing = [edge for edge in e if edge[0] == cur]

            for c in outgoing:
                if _cycle(c[1]):
                    return True
            mid.remove(cur)
            end.add(cur)

    for x in v:
        if x in end:
            continue

        if _cycle(x):
            return True

    return False


def longest(v, e):

    def _reach_all(cur):
        outgoing = [edge for edge in e if edge[0] == cur]
        dists = [1 + _reach_all(x[1]) for x in outgoing]
        return max(dists) if len(dists) else 0

    return max([_reach_all(x) for x in v])


def generate_graph(vertices, max_length, minimum_edges):

    v = set()
    e = set()

    tentative_e = set()

    def generate_vertex():

        name = ""
        while len(name) < 3:
            name += random.choice(ascii_uppercase)
            if name in v:
                name = ""
        return name

    def generate_valid_edge(from_set, to_set):

        while True:

            viable = set([edge for edge in tentative_e if edge[0] in from_set and edge[1] in to_set])

            assert len(viable) > 0, "No possible edges!"

            temp = random.choice(list(viable))
            tentative_e.remove(temp)

            if cycle(v, e | {temp}):
                continue

            elif longest(v, e | {temp}) >= max_length:
                continue

            return temp

    while len(v) < vertices:
        v.add(generate_vertex())
        print("Generating vertices... {} of {} : ({:.2f}%)".format(len(v), vertices, len(v) / vertices * 100), end='\r')
    print()

    tentative_e = set(itertools.product(v, v))
    inner = set(random.choice(list(v)))

    def insert_edge(edge):
        inner.update(edge)
        e.add(edge)
        print("Generating edges... {} of {} : ({:.2f}%)".format(len(e), minimum_edges, len(e) / minimum_edges * 100), end='\r')

    while len(inner) < len(v):
        insert_edge(generate_valid_edge(list(v - inner), v))

    while len(e) < minimum_edges:
        insert_edge(generate_valid_edge(v, v))
    print()

    return Graph(v, e)


def randomized_latent_variables(g: Graph):
    roots = g.roots()
    return random.choices(list(roots), k=random.randrange(1, len(roots)+1))
