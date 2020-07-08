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

try:
    from config.primary_configuration import *
    from utilities.IterableIndexSelection import *

except ModuleNotFoundError:
    print("Uh-oh: Can't import some project modules. Try running this directly in PyCharm.")
    exit(-1)

# Root of the project; fix any relative naming conflicts
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Output some superfluous information only if we are directly running this file
directly_run = __name__ == "__main__"

# Default configuration file directory and name
config_dir = root + "/" + "config"
config_file = "config.json"

# A dictionary to hold all the settings;
#   For CLI overrides, we abstract accessing parameters through "access", never direct indexing.
loaded_settings: dict

# Used such that configuration-file-specified settings can be overridden by a CLI flag
cli_flag_overrides = dict()

# This is the "defaults" configuration file, generated from the primary copy located
#   in config/primary... Used to validate settings
lookup = dict()
for section in primary_config_file:
    for parameter in section["parameters"]:
        p = parameter["parameter"]
        lookup[p] = {
            "default": parameter["default_value"],
            "options": parameter["options"]
        }


def default_value(param: str):
    """
    Get the default setting for a given parameter
    :param param:
    :return: The default value/setting
    """
    return lookup[param]["default"]


def is_valid_option(param: str) -> bool:
    """
    Determine whether a given parameter has a valid setting stored
    :param param: The key of the parameter
    :return: True if the option is valid, False otherwise
    """
    # Strings as "options" indicates a message rather than an actual value
    if isinstance(lookup[param]["options"], str):
        # Looking for any positive number
        if lookup[param]["options"] == "any positive integer":
            return isinstance(loaded_settings[param], int) and loaded_settings[param] > 0

        # Just looking for a path
        else:
            return True

    return isinstance(loaded_settings[param], type(default_value(param)))


def generate_default_configuration_file() -> dict:
    """
    Generate and return a new, "fresh" configuration file
    :return: A dictionary representing a default configuration file
    """
    # Iterate through the primary copy and each "section", and each param in each section
    default_configuration_file = dict()
    for sec in primary_config_file:
        for param in sec["parameters"]:
            key = param["parameter"]
            default_configuration_file[key] = param["default_value"]
    return default_configuration_file


def initialize_configuration_file():
    """
    Create a default/vanilla config file if it does not already exist
    """

    # The directory doesn't exist; make it
    if not os.path.isdir(config_dir):
        print("Default configuration directory not found...", end="")
        os.makedirs(config_dir)
        print("Created.")
    elif directly_run:
        print("Default configuration directory already exists.")

    # The file doesn't exist; make it
    if not os.path.isfile(config_dir + "/" + config_file):
        print("Default configuration file not found...", end="")

        # The default configuration file will be generated from the primary version
        with open(config_dir + "/" + config_file, "w") as f:
            json.dump(generate_default_configuration_file(), f, indent=4, sort_keys=True)
        print("Created.")
    elif directly_run:
        print("Default configuration file already exists.")

    load_configuration_file()


def delete_configuration_file():
    """
    Delete the configuration file
    """
    if os.path.isfile(config_file):
        os.remove(config_dir + "/" + config_file)
        print("Configuration file deleted.")
    else:
        print("Couldn't find configuration file.")


def repair_configuration_file():
    """
    Attempt to repair a configuration file if it an error is detected, such as a missing parameter, or invalid option.
    """
    # See if any settings have failed
    errors = False

    def set_default(reset_key):
        loaded_settings[reset_key] = lookup[reset_key]["default"]

    for key in lookup:
        if key not in loaded_settings:
            print("Missing configuration setting for:", key)
            set_default(key)
            errors = True

        if not is_valid_option(key):
            setting_is = str(loaded_settings[key]) + "|" + str(type(loaded_settings[key]))
            setting_should = str(lookup[key]["default"])
            print("Parameter:", key, "has unsupported option:", setting_is + "\nUsing default value:", setting_should)
            set_default(key)
            errors = True

    # Store the new version of the configuration file
    with open(config_dir + "/" + config_file, "w") as f:
        json.dump(loaded_settings, f, indent=4, sort_keys=True)

    # Reload if any errors
    if errors:
        print("Some errors were detected and repaired; reloading configuration file.")
        load_configuration_file()
    else:
        print("No errors found.")


def load_configuration_file():
    """
    Load the configuration file from the stored JSON file
    """
    # Load the configuration file
    global loaded_settings
    with open(config_dir + "/" + config_file) as config:
        loaded_settings = json.load(config)


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
    if param not in loaded_settings:
        print("\nConfiguration Lookup Error;\nCouldn't find parameter: " + param + "\n" +
              "Re-generating configuration file...")
        repair_configuration_file()
        initialize_configuration_file()

    # See if the configuration file has an invalid setting for this, and repair if so
    if not is_valid_option(param):
        print("Error on key:", param)
        print("Repairing configuration file.")
        repair_configuration_file()

    # A default has been specified in the configuration file
    value = loaded_settings[param]

    # A CLI flag has been provided to override the config file
    if param in cli_flag_overrides:
        value = parsed_args.param

    return value


# This file is being run directly
if __name__ == "__main__":

    print("Opened the configuration file manager.\n")

    options = [
        [initialize_configuration_file, "Initialize a configuration file if it doesn't exist"],
        [delete_configuration_file, "Delete the current configuration file"],
        [repair_configuration_file, "Repair missing/invalid configuration options without affecting other options."],
        [exit, "Exit"]
    ]

    while True:

        # Get a selection from the above options
        selection = user_index_selection("Select an option:", options)

        print()     # Aesthetic spacing

        # Run selected option
        options[selection][0]()
