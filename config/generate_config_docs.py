#!/usr/bin/env python

#########################################################
#                                                       #
#   Generate Configuration Documentation                #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Run this file directly to update documentation on configuration files

import os
from config.primary_configuration import *

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
documentation_file = root + "/documentation/configuration.md"


def generate_configuration_documentation():
    """
    Generates the markdown file for configuration file documentation
    """
    # Delete it if it exists; making a new one
    if os.path.isfile(documentation_file):
        os.remove(documentation_file)

    with open(documentation_file, "w") as f:

        # Title of the file
        f.write("# Configuration File Settings\n\n")

        # The master file is structured as a list of sections
        for category in primary_config_file:

            # Subtitle and description
            f.write("## " + category["section"] + "\n\n")
            f.write(category["description"] + "\n\n")

            # Write each parameter as its own "sub-sub-section"
            for parameter in category["parameters"]:
                f.write("#### " + parameter["parameter_title"] + "\n\n")
                f.write(parameter["description"] + "\n\n")

                # This is the header/markdown required for a table
                f.write("| Setting Name | Options | Default Value |\n|:-:|:-:|:-:|\n")
                f.write("| " + parameter["parameter"] + " | " + str(parameter["options"]) + " | " + str(parameter["default_value"]) + " |\n\n")


if __name__ == "__main__":
    generate_configuration_documentation()
