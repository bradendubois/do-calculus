#!/usr/bin/env python

# Run this file directly to update documentation on configuration files

from pathlib import Path

from .primary_configuration import primary_config_file

documentation_file = Path(".", "doc", "Configuration.md")


def generate_configuration_documentation():
    """
    Generates the markdown file for configuration file doc
    """

    with documentation_file.open("w") as f:

        # Title of the file
        f.write("# Configuration File Settings\n\n")
        f.write("Settings for the project are stored in ``src/config/config.yml``.\n")
        f.write("- **Note**: This file will be created if it does not exist, when the project is run.\n\n")

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
                f.write("| ``" + parameter["parameter"] + "`` | " + str(parameter["options"]))
                f.write(" | " + str(parameter["default_value"]) + " |\n\n")


if __name__ == "__main__":
    generate_configuration_documentation()
