#########################################################
#                                                       #
#   config manager                                      #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

import json         # Settings data is stored in JSON
import os           # Used to create a directory/config file if not found
import argparse     # Allow command-line flag parsing

from config.primary_configuration import *

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Default configuration file directory and name
config_dir = root + "/" + "config"
config_file = "config.json"

# A dictionary to hold all the settings;
#   For CLI overrides, we abstract accessing parameters through "access", never direct indexing.
settings: dict

# Used such that configuration-file-specified settings can be overridden by a CLI flag
cli_flag_overrides = dict()

# This is the "defaults" configuration file, generated from the primary copy located in config/primary...
defaults = dict()

# This is an actual vanilla configuration file, dumped to a .json file if there isn't one
default_file = dict()

for section in primary_config_file:
    for parameter in section["parameters"]:
        param_key = parameter["parameter"]
        defaults[param_key] = dict()
        defaults[param_key]["default"] = parameter["default_value"]
        defaults[param_key]["options"] = parameter["options"]
        default_file[param_key] = parameter["default_value"]


def initialize_configuration_file():
    """
    Create a default/vanilla config file if it does not already exist
    """

    # The directory doesn't exist; make it
    if not os.path.isdir(config_dir):
        print("Default configuration directory not found...", end="")
        os.makedirs(config_dir)
        print("Created.")

    # The file doesn't exist; make it
    if not os.path.isfile(config_dir + "/" + config_file):
        print("Default configuration file not found...", end="")

        # The default configuration file will be generated from the primary version
        with open(config_dir + "/" + config_file, "w") as f:
            json.dump(default_file, f, indent=4, sort_keys=True)
        print("Created.")

    # Load the configuration file
    global settings
    with open(config_dir + "/" + config_file) as config:
        settings = json.load(config)


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


# Always initialize/load the configuration load
initialize_configuration_file()

# Create parser for CLI flags to override config settings
parsed_args = cli_arg_parser()


def access(param: str) -> any:
    """
    Access a configuration-file setting, if it exists, or has a CLI flag given as an override.
    :param param: The string key for the setting
    :return: The specified value, first checking CLI flags, then config file.
    """

    # Quick Check; if the param specified isn't found, maybe the config file is outdated
    if param not in settings:
        print("\nConfiguration Lookup Error;\nCouldn't find parameter: " + param + "\n" +
              "Re-generating configuration file...")
        os.remove(config_dir + "/" + config_file)
        initialize_configuration_file()

    # By default, assume nothing
    value = None

    # A default has been specified in the configuration file
    if param in settings:

        # A string is used to just say "must be a positive integer"; don't check those
        if not isinstance(defaults[param]["options"], str):

            # Unsupported option given
            if settings[param] not in defaults[param]["options"]:
                print("Parameter: " + param + " has unsupported option: " + str(settings[param]) + "|" +
                      str(type(settings[param])) + "\nUsing default value: " + str(defaults[param]["default"]))
                value = defaults[param]["default"]
            else:
                value = settings[param]
        else:
            value = settings[param]

    # A CLI flag has been provided to override the config file
    if param in cli_flag_overrides:
        value = parsed_args.param

    return value
