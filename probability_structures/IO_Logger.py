#########################################################
#                                                       #
#   IO Logger                                           #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

from config.config_mgr import *


class IOLogger:

    file = None

    def open(self, filename):
        """
        Open a specified file in the default logging location
        :param filename: The name of the file to open
        """

        # Close any open file
        if self.file:
            self.close()

        # Open new file in write mode
        self.file = open(access("logging_directory") + "/" + filename, "w")

    def close(self):
        """
        Close the currently opened file, if any.
        """

        if self.file:
            self.file.close()

    def write(self, *message: str, join=" ", end="\n", x_offset=0):
        """
        Optional output of any number of strings unless output is suppressed
        :param message: Any number of strings to print
        :param join: A string used to join the messages
        :param end: The end symbol outputted at the end of the series of strings
        :param x_offset: The amount of space at the beginning of every line to indent by
        :return:
        """

        indent = int(x_offset) * "  "

        if access("output_computation_steps"):
            print("\n" + indent, end="")

        if self.file:
            self.file.write("\n" + indent)

        for component in message:

            if access("output_computation_steps"):
                print(str(component).replace("\n", "\n" + indent, 100), end=join)

            if self.file:
                self.file.write(str(component).replace("\n",  "\n" + indent, 100) + join)

        if access("output_computation_steps"):
            print(end=end)

        if self.file:
            self.file.write(end)


io = IOLogger()
