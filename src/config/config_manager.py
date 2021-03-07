#########################################################
#                                                       #
#   config manager                                      #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

from yaml import safe_load as load, dump
import os           # Used to create a directory/config file if not found
import argparse     # Allow command-line flag parsing

from src.config.primary_configuration import *

# Root of the project; fix any relative naming conflicts
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Default configuration file directory and name
config_dir = root + "/" + "config"
config_file = "config.yml"


def create_default():

    # This is the "defaults" configuration file, generated from the primary copy located
    #   in config/primary... Used to validate settings
    d = dict()
    for section in primary_config_file:
        for parameter in section["parameters"]:
            d[parameter["parameter"]] = parameter["default_value"]

    return d


# Used such that configuration-file-specified settings can be overridden by a CLI flag
cli_flag_overrides = dict()


def cli_arg_parser() -> argparse.Namespace:
    """
    Create a basic CLI flag parser to override the config file settings
    :return: an argparse.Namespace object, with flag values accessed as "parser.FLAG"
    """

    # TODO - More flags will be added
    arg_params = [
        {
            "flag": "-s",
            "help": "Silent computation: only show resulting probabilities.",
            "action": "store_true",
            "override_setting": "output_computation_results"
        },
        {
            "flag": "-c",
            "help": "Cache computation results; speeds up subsequent queries.",
            "action": "store_true",
            "override_setting": "cache_computation_results"
        }
    ]

    parser = argparse.ArgumentParser(description="Compute probabilities and resolve backdoor paths.")

    # Add each flag as listed above into the parser
    for param in arg_params:
        parser.add_argument(param["flag"], help=param["help"], action=param["action"])

        if "override_setting" in param:
            cli_flag_overrides["override_setting"] = param["flag"][1:]

    # Parse all given, constructing and returning a Namespace object
    return parser.parse_args()


# Create parser for CLI flags to override config settings
# parsed_args = cli_arg_parser()

default = create_default()

# No configuration file found - create one
if not os.path.isfile(config_dir + "/" + config_file):

    with open(config_dir + "/" + config_file, "w") as f:
        dump(default, f, indent=4, sort_keys=True)

# Load the settings file
with open(config_dir + "/" + config_file) as config:
    settings_yml = load(config)
