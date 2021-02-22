from probability.structures.CausalGraph import CausalGraph
from probability.structures.VariableStructures import *
from config.config_manager import *
from datetime import *

cache_times = []

loaded_settings["cache_computation_results"] = True

loaded_settings["topological_sort_variables"] = True

for _ in range(20):
    cg = CausalGraph("../full/causal_graph_5.json")

    start = datetime.now()
    cg.probability([Outcome("Xj", "xj")], [])
    finish = datetime.now()

    cache_times.append((finish-start).microseconds)

no_cache_times = []

loaded_settings["topological_sort_variables"] = False

for _ in range(20):
    cg = CausalGraph("../full/causal_graph_5.json")

    start = datetime.now()
    cg.probability([Outcome("Xj", "xj")], [])
    finish = datetime.now()

    no_cache_times.append((finish-start).microseconds)

print("Average w/  caching:", str(sum(cache_times)/len(cache_times)))
print("Average w/o caching:", str(sum(no_cache_times)/len(no_cache_times)))
