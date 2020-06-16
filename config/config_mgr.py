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

    default_configuration_file = {
        "runRegressionTestsOnLaunch": True,
        "outputRegressionResults": "failure",
        "output_computation_steps": False,
        "exitIfRegressionFailure": False,
        "graph_file_folder": "causal_graphs",
        "logAllComputation": True,
        "loggingLocation": "logging",
        "storeAllResolvedCalculations": True,
        "defaultRegressionRepetition": 10,
        "printCausalGraphInfoOnInstantiation": True
    }

    if not os.path.isdir(config_dir):
        print("Default configuration directory not found...", end="")
        os.makedirs(config_dir)
        print("Created.")

    if not os.path.isfile(config_dir + "/" + config_file):
        print("Default configuration file not found...", end="")
        with open(config_dir + "/" + config_file, "w") as f:
            json.dump(default_configuration_file, f)
        print("Created.")


def cli_arg_parser() -> argparse.Namespace:

    arg_params = [
        {
            "flag": "-s",
            "help": "Silent computation: only show resulting probabilities.",
            "action": "store_true"
        }
    ]

    parser = argparse.ArgumentParser(description="Compute probabilities.")

    for param in arg_params:
        parser.add_argument(param["flag"], help=param["help"], action=param["action"])
    return parser.parse_args()


# Always try to initialize if not found
initialize_configuration_file()

# Parser for CLI flags to override config settings
parsed_args = cli_arg_parser()

# Load the configuration file
with open(config_file) as config:
    settings = json.load(config)


def access(param: str) -> any:
    if param in settings:
        return settings[param]

# TODO - A function for config settings can let you do command-line flags to override the config file


def silent_computation() -> bool:
    return parsed_args.s or settings["output_computation_steps"]



def run_regression_tests_on_launch():
    return settings["runRegressionTestsOnLaunch"]


def output_regression_computation():
    return settings["outputRegressionComputation"]

