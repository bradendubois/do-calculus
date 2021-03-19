from typing import Collection, Dict, List, Set

from ..structures.BackdoorController import BackdoorController
from ..structures.Types import Vertices


def api_deconfounding_sets_parse(query: str) -> Dict[str, Collection[str]]:
    """
    Convert a given query string into a pair of sets to find all sufficient deconfounding sets between.
    @param query: A string of the form "X, Y, Z -> A, B, C"
    @return A dictionary of keys "src" and "dst" mapped to sets containing all vertices (as strings) on the left and
        right sides of the arrow, respectively.
    """
    def clean(x):
        return set(map(lambda y: y.strip(), x.strip().split(",")))

    src, dst = map(clean, query.split("->"))

    return {
        "src": src,
        "dst": dst
    }


def api_deconfounding_sets(bc: BackdoorController, src: Vertices, dst: Vertices) -> List[Set[str]]:
    """
    Compute and return all the backdoor paths from any vertex in src to any vertex is dst
    @param bc: A Backdoor Controller with a graph conforming to the given source and destination sets.
    @param src: A set of string vertices that are in the given Backdoor Controller, which will be the vertices to
        attempt to connect to vertices in dst by a backdoor path (s).
    @param dst: A set of string vertices that are in the given Backdoor Controller, which will be reached by vertices
        in src.
    @return a list of sets, where each set - a set of string vertices - is sufficient at blocking all backdoor paths
        from any vertex in src to any other vertex in dst.
    """
    return bc.all_dcf_sets(src, dst)
