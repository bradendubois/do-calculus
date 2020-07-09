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
logging_dir = root + "/" + access("logging_directory")
regression_subdir = logging_dir + "/" + access("regression_log_subdirectory")


class IOLogger:

    file = None

    # Used as a way of disabling or suppressing IO/Writing during testing
    console_enabled = True

    # Lock where stuff is logged if we are in regression tests; all text should also go to one file
    lock_stream_switch = False

    def open(self, filename):
        """
        Open a specified file in the default logging location
        :param filename: The name of the file to open
        """

        # Don't switch files if we are in a regression mode
        if self.lock_stream_switch:
            return

        # Close any open file
        if self.file:
            self.close()

        # Create the general logging directory (if needed)
        if not os.path.isdir(logging_dir) and access("log_computation"):
            os.makedirs(logging_dir)

        # Create the regression test subdirectory (if needed)
        if not os.path.isdir(regression_subdir) and access("log_all_regression_computation"):
            os.makedirs(regression_subdir)

        # Open new file in write mode
        self.file = open(logging_dir + "/" + filename, "w")

    def close(self):
        """
        Close the currently opened file, if any.
        """
        if self.lock_stream_switch:
            return

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
        """
        # Slight check; if there is nothing to actually be written anywhere, just exit early
        if not (self.console_enabled or access("output_computation_steps") or console_override or self.file):
            return

        # We can put this indent in front of each line of the message passed; this allows us to detect the recursive
        #   "depth" of our queries, and pass it as a parameter to horizontally offset a message here rather than
        #   fiddle with that where it's being called/printed
        indent = int(x_offset) * "  "

        # Give some spacing in the terminal between messages
        if self.console_enabled and access("output_computation_steps") or console_override:
            print("\n" + indent, end="")

        # Same as above, but with whatever file could be open
        if self.file:
            self.file.write("\n" + indent)

        # Write each component, bit by bit, where we replace newlines with newlines + that horizontal indentation
        for component in message:

            # 100 is the arbitrary limit I've placed on how many newlines can get replaced, since if it's absent, it
            #   only replaces the first occurrence, but there'd never be 100+ in one message.

            if self.console_enabled and access("output_computation_steps") or console_override:
                print(str(component).replace("\n", "\n" + indent, 100), end=join)

            if self.file:
                self.file.write(str(component).replace("\n",  "\n" + indent, 100) + join)

        if self.console_enabled and access("output_computation_steps") or console_override:
            print(end=end)

        if self.file:
            self.file.write(end)

    def disable_console(self):
        """
        Disable the console-outputting of the IO Logger
        """
        self.console_enabled = False

    def enable_console(self):
        """
        Enable the console-outputting of the IO Logger
        """
        self.console_enabled = True


io = IOLogger()
