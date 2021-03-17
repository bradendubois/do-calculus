from yaml import safe_load as load
from pathlib import Path

from .api.backdoor_paths import api_backdoor_paths_parse
from .api.deconfounding_sets import api_deconfounding_sets_parse
from .api.probability_query import api_probability_query_parse

from .API import Do


# TODO - Change graph_location to allow a specific graph to be given and loaded, or specify a user directory without
#   there being path issues depending on the working directory


def main(graph_location=Path(".", "graphs")):
    """
    Run an interactive IO prompt allowing full use of the causality software.
    @param graph_location: A string of the path from the working directory to a directory of graphs
        which are JSON files and conform to the causal graph model specification.
    """
    def skip(*args, **kwargs):
        return {}

    api = Do(model=None, print_detail=False, print_result=True)

    """
    This is a mapping that will connect user-inputting strings to the respective functionality requested.

    This behaves as a tuple -> list dictionary, where the tuple contains two arbitrary functions, and the
    list contains all lowercase strings which, if given as input, should result in the respective tuple's
    functions being called.

    The tuple contains two functions that behave as follows:
    - The first function must take exactly one string as an argument, and it is responsible for parsing this
    string into any arbitrary type(s) required by the second function.
    - The second function is the "real" function, where the first function always behaves as a parser/cleaner.
    - The first function should always return a dictionary, where the keys of the dictionary match the parameters
    of the second function, to allow the results of the parsing to always be unpacked into the second function
    """
    api_map = {
        (api_probability_query_parse, api.p): ["probability", "p", "compute", "query"],
        (api_deconfounding_sets_parse, api.deconfounding_sets): ["dcs", "dcf", "deconfound", "deconfounding"],
        (api_backdoor_paths_parse, api.backdoor_paths): ["backdoor", "backdoors", "path", "paths"],
        (skip, api.joint_distribution_table): ["jdt", "joint"]
    }

    help_options = ["?", "help", "options"]
    list_options = ["list", "all", "see", "l", "ls"]
    load_options = ["load", "import", "start", "graph"]
    exit_options = ["quit", "exit", "stop", "leave", "q"]

    assert len(set().union(*api_map.values())) == sum(map(len, api_map.values())), \
        "Conflicting keywords; one input maps to more than two possible options!"

    # Construct dictionary mapping input -> api functions
    lookup = dict()
    for f, v in api_map.items():
        lookup.update({k: f for k in v})

    while user_str := input(">> ").strip().split(" ", 1):

        f = user_str[0].lower().strip()
        arg = user_str[1].strip() if len(user_str) == 2 else ""

        # Help / List options
        if f in help_options:
            print("")

        # List all possible graphs (ignores the generated models used for debugging / testing)
        if f in list_options:
            assert graph_location.is_dir(), \
                "The specified directory for causal graph models {} does not exist!".format(graph_location.name)

            files = filter(lambda g: g.suffix.lower() == ".yml", sorted(graph_location.iterdir()))
            print("Options", *list(map(lambda file: file.stem, files)), sep="\n- ")
            continue

        # Parse and load a model into the API
        if f in load_options:
            s = arg + (".yml" if not arg.endswith(".yml") else "")
            assert (full_path := graph_location / s).is_file(), \
                "File: {} does not exist!".format(s)

            with full_path.open("r") as f:
                api.load_model(load(f))
            continue

        # Quit / Close
        if f in exit_options:
            break

        # ??? Unknown input
        if f not in lookup:
            print("Error; input not in options.")  # TODO - Try 'help' or '?' for options.")
            continue

        # parse === string parser, func === api function
        parse, func = lookup[f]

        # Parse input, call api function
        # try:
        func(**parse(arg))
        # except Exception as e:
        #    print("EXCEPTION:", str(e))
