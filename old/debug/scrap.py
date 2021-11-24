from pathlib import Path
from do.structures.Graph import Graph
from yaml import safe_dump

from markov_generator.gen_distribution import generate_distribution
from markov_generator.gen_markov_model import semi_markov_transform

V = {"U", "X", "Z", "Y"}
E = {("U", "X"), ("U", "Y"), ("X", "Z"), ("Z", "Y")}

G = Graph(V, E)

# Observable version

distribution = generate_distribution(G)

P = Path("../tests/modules/shpitser/models/markov/3.6smoking.yml")

with P.open("w") as f:
    safe_dump({
        "name": "3.6 - Smoking Genotype (Observable)",
        "model": distribution
    }, f)

# Latent U version

latent_model = semi_markov_transform({"model": distribution}, k=1)

P = Path("../tests/modules/shpitser/models/semi_markov/3.6smoking_L.yml")

with P.open("w") as f:
    safe_dump({
        "name": "3.6 - Smoking Genotype (Unobservable)",
        "model": latent_model
    }, f)
