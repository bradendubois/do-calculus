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

# Default configuration file directory and name
config_dir = "config"
config_file = "config.json"


def initialize_configuration_file():
    """
    Create a default/vanilla config file if it does not already exist
    """

    # The default values for the config file; updating these won't apply to an already-created file
    default_configuration_file = {

        "run_regression_tests_on_launch": True,
        "output_regression_results": "failure",
        "output_computation_steps": False,
        "exit_if_regression_failure": False,
        "graph_file_folder": "causal_graphs",
        "log_computation": True,
        "logging_directory": "logging",
        "cache_computation_results": False,
        "default_regression_repetition": 10,
        "print_cg_info_on_instantiation": True,
        "regression_directory": "regression_tests/test_files",
        "regression_levels_of_precision": 5,
        "output_levels_of_precision": 5
    }

    # The directory doesn't exist; make it
    if not os.path.isdir(config_dir):
        print("Default configuration directory not found...", end="")
        os.makedirs(config_dir)
        print("Created.")

    # The file doesn't exist; make it
    if not os.path.isfile(config_dir + "/" + config_file):
        print("Default configuration file not found...", end="")
        with open(config_dir + "/" + config_file, "w") as f:
            json.dump(default_configuration_file, f)
        print("Created.")


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


# Always try to initialize if not found
initialize_configuration_file()

# Create parser for CLI flags to override config settings
parsed_args = cli_arg_parser()

# Load the configuration file
with open(config_dir + "/" + config_file) as config:
    settings = json.load(config)


def access(param: str) -> any:
    """
    Access a configuration-file setting, if it exists, or has a CLI flag given as an override.
    :param param: The string key for the setting
    :return: The specified value, first checking CLI flags, then config file.
    """

    # By default, assume nothing
    value = None

    # A default has been specified in the configuration file
    if param in settings:
        value = settings[param]

    # A CLI flag has been provided to override the config file
    if param in cli_flag_overrides:
        value = parsed_args.param

    return value
