from yaml import safe_load as load, dump
from os.path import abspath, dirname, isfile

from src.config.primary_configuration import *

# Root of the project; fix any relative naming conflicts
root = dirname(dirname(abspath(__file__)))

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


# No configuration file found - create one
if not isfile(config_dir + "/" + config_file):

    with open(config_dir + "/" + config_file, "w") as f:
        dump(create_default(), f, indent=4, sort_keys=True)

# Load the settings file
with open(config_dir + "/" + config_file) as config:
    settings_yml = load(config)
