from pathlib import Path
from yaml import safe_load as load, dump

from ..config.primary_configuration import primary_config_file

path = Path(".", "config.yml")


def create_default():

    # This is the "defaults" configuration file, generated from the primary copy located
    #   in config/primary... Used to validate settings
    d = dict()
    for section in primary_config_file:
        for parameter in section["parameters"]:
            d[parameter["parameter"]] = parameter["default_value"]

    return d


# No configuration file found - create one
if not path.is_file():

    with path.open("w") as f:
        dump(create_default(), f, indent=4, sort_keys=True)

# Load the settings file
with path.open("r") as config:
    settings_yml = load(config)
