from itertools import product

from src.probability.structures.BackdoorController import BackdoorController


def api_deconfounding_sets_parse(query: str) -> (set, set):
    """
    Convert a given query string into a pair of sets to find all sufficient deconfounding sets between.

    Parameters
    ----------
    query: A string of the form "X, Y, Z -> A, B, C"

    Returns
    -------
    Two sets, containing all variables on the left and right sides of the arrow, respectively.
    """
    def clean(x):
        return set(map(x.strip(), x))

    return map(clean, query.split("->"))


def api_deconfounding_sets_paths(bc: BackdoorController, src: set, dst: set) -> list:
    """
    Compute and return all the backdoor paths from any vertex in src to any vertex is dst

    Parameters
    ----------
    bc: A Backdoor Controller with a graph conforming to the given source and destination sets.
    src: A set of string vertices that are in the given Backdoor Controller, which will be the vertices
        to attempt to connect to vertices in dst by a backdoor path (s).
    dst: A set of string vertices that are in the given Backdoor Controller, which will be reached by
        vertices in src.

    Returns
    -------
    Returns a list of sets, where each set - a set of string vertices - is sufficient at blocking all
        backdoor paths from any vertex in src to any other vertex in dst.
    """
    return bc.get_all_z_subsets(src, dst)
