from pathlib import Path

from do.shpitser.latent.LatentProjection import latent_projection
from do.shpitser.structures.JointDistribution import JointDistribution
from do.shpitser.structures.LatentGraph import LatentGraph
from do.structures.CausalGraph import CausalGraph
from do.util.ModelLoader import parse_model
from do.shpitser.identification.IDAlgorithm import ID

mark = Path("tests/modules/shpitser/models/markov/3.6smoking.yml")

semi_mark = Path("tests/modules/shpitser/models/semi_markov/3.6smoking_L.yml")

mark_model = parse_model(mark)
semi_mark_model = parse_model(semi_mark)

mark_cg = CausalGraph(**mark_model)
semi_mark_cg = CausalGraph(**semi_mark_model)

s = ID({"Y"}, {"X"}, JointDistribution(semi_mark_cg.tables), latent_projection(mark_cg.graph, {"U"}))

print(s)
