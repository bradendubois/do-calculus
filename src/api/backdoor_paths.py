from itertools import product

from src.probability.structures.BackdoorController import BackdoorController


def api_backdoor_paths_parse(query: str) -> (set, set):
    """
    Convert a given query string into a pair of sets to compute all backdoor paths between
    @param query: A string of the form "X, Y, Z -> A, B, C"
    @return Two sets, containing all variables on the left and right sides of the arrow, respectively.
    """
    def clean(x):
        return set(map(x.strip(), x))

    l, r = query.split("->")
    r, dcf = map(clean, r.split("|")) if "|" in r else clean(r), {}
    return clean(l), r, dcf


def api_backdoor_paths(bc: BackdoorController, src: set, dst: set, dcf: set) -> list:
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
    # TODO Add a method in Backdoor Controller that can return all paths immediately
    paths = []
    for s, t in product(src, dst):
        paths += bc.backdoor_paths(s, t, dcf)
    return paths
