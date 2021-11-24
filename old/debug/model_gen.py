from random import randrange
from gen_markov_model import create_k_models

i = 10

while i:
    num_vertices = randrange(5, 15)
    max_path_length = randrange(round(.2 * num_vertices), round(.8 * num_vertices))
    num_edges = randrange(num_vertices - 1, round(3 * num_vertices))

    i -= create_k_models(i, "output", 1, num_vertices, max_path_length, num_edges)
