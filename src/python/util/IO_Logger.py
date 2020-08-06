#########################################################
#                                                       #
#   IO Logger                                           #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

from python.config.config_manager import *

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logging_dir = root + "/" + access("logging_directory")
regression_subdir = logging_dir + "/" + access("regression_log_subdirectory")


class IOLogger:

    file = None

    # Used as a way of disabling or suppressing IO/Writing during testing
    console_enabled = True

    # Lock where stuff is logged if we are in regression tests; all text should also go to one file
    lock_stream_switch = False

    # A flag to toggle that we are in a regression testing mode, which can alter what is output
    regression_mode = False

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

    def write(self, *message: str, join=" ", end="\n", x_offset=0):
        """
        Optional output of any number of strings to the terminal
        :param message: Any number of strings to print
        :param join: A string used to join the messages
        :param end: The end symbol outputted at the end of the series of strings
        :param x_offset: The amount of space at the beginning of every line to indent by
        """

        # Save whatever file we might have open, and clear it from the logger
        restore = self.file
        self.file = None

        # Write the message to the console, without it being written to the file
        self.write_log(*message, join=join, end=end, x_offset=x_offset, override=True)

        # Restore any file we might've had open
        self.file = restore

    def write_log(self, *message: str, join=" ", end="\n", x_offset=0, override=False):
        """
        Output of any number of strings to the terminal as well as an open log file
        :param message: Any number of strings to print
        :param join: A string used to join the messages
        :param end: The end symbol outputted at the end of the series of strings
        :param x_offset: The amount of space at the beginning of every line to indent by
        :param override: Whether to output the message to console regardless of internal settings
        """

        # Flags that can be a valid reason to output to the terminal
        regression_output = self.regression_mode and access("output_regression_test_computation")

        computation_output = not self.regression_mode and access("output_computation_steps")
        computation_log = not self.regression_mode and access("log_computation")

        io_override = override and not self.regression_mode

        # Check if we're in either mode to be logging data
        if not regression_output and not computation_output and not computation_log and not io_override:
            return

        # We can put this indent in front of each line of the message passed; this allows us to detect the recursive
        #   "depth" of our queries, and pass it as a parameter to horizontally offset a message here rather than
        #   fiddle with that where it's being called/printed
        indent = int(x_offset) * "  "

        # Give some spacing in the terminal between messages
        if regression_output or computation_output or io_override:
            print("\n" + indent, end="")

        # Same as above, but with whatever file could be open
        if self.file:
            self.file.write("\n" + indent)

        # Write each component, bit by bit, where we replace newlines with newlines + that horizontal indentation
        for component in message:

            # 100 is the arbitrary limit I've placed on how many newlines can get replaced, since if it's absent, it
            #   only replaces the first occurrence, but there'd never be 100+ in one message.
            if regression_output or computation_output or io_override:
                print(str(component).replace("\n", "\n" + indent, 100), end=join)

            if self.file and computation_log:
                self.file.write(str(component).replace("\n",  "\n" + indent, 100) + join)

        if regression_output or computation_output or io_override:
            print(end=end)

        if self.file:
            self.file.write(end)


io = IOLogger()
