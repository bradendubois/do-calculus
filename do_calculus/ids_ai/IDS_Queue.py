#########################################################
#                                                       #
#   IDS Queue                                           #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# This will serve as a pretty standard queue / option system for your typical iterative deepening search (IDS).
#   Thanks, Professor Horsch, for CMPT 317!

from config.config_manager import access


class IDSQueue:

    def __init__(self):
        """
        A basic initializer for an empty queue
        """

        self.queue = []
        self.depth_limit = access("ids_initial_limit")

    def next(self):
        if len(self.queue) > 0:
            return self.queue.pop(0)

    def empty(self):
        return len(self.queue) == 0

    def enqueue(self, item):
        self.queue.append(item)


class Item:
    pass
