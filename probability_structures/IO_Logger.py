#########################################################
#                                                       #
#   IO Logger                                           #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

import os
from config.config_manager import *

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class IOLogger:

    file = None

    # Used as a way of disabling or suppressing IO/Writing during testing
    console_enabled = True

    def open(self, filename):
        """
        Open a specified file in the default logging location
        :param filename: The name of the file to open
        """

        # Close any open file
        if self.file:
            self.close()

        # Create directory if needed
        if not os.path.isdir(root + "/" + access("logging_directory")):
            os.makedirs(root + "/" + access("logging_directory"))
            os.makedirs(root + "/" + access("logging_directory") + "/" + access("regression_log_subdirectory"))

        # Open new file in write mode
        self.file = open(root + "/" + access("logging_directory") + "/" + filename, "w")

    def close(self):
        """
        Close the currently opened file, if any.
        """
        if self.file:
            self.file.write("\n\n" + 50 * "*" + "\n\n")
            self.file.close()
        self.file = None

    def write(self, *message: str, join=" ", end="\n", x_offset=0, console_override=False):
        """
        Optional output of any number of strings unless output is suppressed
        :param message: Any number of strings to print
        :param join: A string used to join the messages
        :param end: The end symbol outputted at the end of the series of strings
        :param x_offset: The amount of space at the beginning of every line to indent by
        :param console_override: An optional flag that ensures info is printed to the console
        :return:
        """
        indent = int(x_offset) * "  "

        if self.console_enabled and access("output_computation_steps") or console_override:
            print("\n" + indent, end="")

        if self.file:
            self.file.write("\n" + indent)

        for component in message:

            if self.console_enabled and access("output_computation_steps") or console_override:
                print(str(component).replace("\n", "\n" + indent, 100), end=join)

            if self.file:
                self.file.write(str(component).replace("\n",  "\n" + indent, 100) + join)

        if self.console_enabled and access("output_computation_steps") or console_override:
            print(end=end)

        if self.file:
            self.file.write(end)

    def disable_console(self):
        self.console_enabled = False

    def enable_console(self):
        self.console_enabled = True


io = IOLogger()
