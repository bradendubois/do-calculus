#########################################################
#                                                       #
#   Stack                                               #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# This will serve as a pretty standard stack for your typical iterative deepening search (IDS).


class Stack:

    def __init__(self):
        """
        A basic initializer for an empty queue
        """

        self.stack = []

    def pop(self):
        if len(self.stack) > 0:
            return self.stack.pop(-1)

    def empty(self):
        return len(self.stack) == 0

    def push(self, item):
        self.stack.append(item)

    def clear(self):
        self.stack.clear()
