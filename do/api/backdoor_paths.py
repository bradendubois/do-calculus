from typing import Collection, Dict, List, Optional

from ..structures.BackdoorController import BackdoorController
from ..structures.Types import Path, Vertices


def api_backdoor_paths_parse(query: str) -> Dict[str, Collection[str]]:
    """
    Convert a given query string into a pair of sets to compute all backdoor paths between
    @param query: A string of the form "X, Y, Z -> A, B, C" or "X, Y, Z -> A, B, C | I, J, K"
    @return A dictionary mapping "src", "dst", and "dcf" to sets, containing all vertices on the left and right sides
        of the arrow, and the third as all vertices are the right of the bar, respectively.
    """
    def clean(x):
        return set(map(lambda y: y.strip(), x.strip().split(",")))

    l, r = query.split("->")

    if "|" in r:
        s = r.split("|")
        r, dcf = clean(s[0]), clean(s[1])
    else:
        r, dcf = clean(r), set()

    return {
        "src": clean(l),
        "dst": r,
        "dcf": dcf
    }


def api_backdoor_paths(bc: BackdoorController, src: Vertices, dst: Vertices, dcf: Optional[Vertices]) -> List[Path]:
    """
    Compute and return all the backdoor paths from any vertex in src to any vertex in dst
    @param bc: A Backdoor Controller with a graph conforming to the given source and destination sets.
    @param src: A set of string vertices that are in the given Backdoor Controller, which will be the vertices to
        attempt to connect to vertices in dst by a backdoor path (s).
    @param dst: A set of string vertices that are in the given Backdoor Controller, which will be reached by vertices
        in src.
    @param dcf: A set of string vertices in the given Backdoor Controller, which will behave as a deconfounding set to
        block paths from src to dst.
    @return all backdoor paths connecting any vertex in src to a vertex in dst, by which each path is represented as a
        list containing each vertex (as a string) from the source vertex to the destination vertex, with dcf acting as
        a deconfounding set.
    """
    return bc.backdoor_paths(src, dst, dcf)
