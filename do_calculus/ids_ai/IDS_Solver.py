#########################################################
#                                                       #
#   Do Calculus Options                                 #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Basic IDS-approach solver taking an initial query and solving until there are no interventions left
#   Thanks, Professor Horsch, for CMPT 317!

from do_calculus.application.DoCalculusOptions import do_calculus_options
from do_calculus.ids_ai.Stack import Stack
from probability_structures.Graph import Graph


class Solution:
    """Wrapper to represent the results of the IDS Searcher"""

    def __init__(self, success: bool, result):
        self.success = success
        self.result = result


class IDSSolver:
    """
    A basic iterative-deepening-search approach to do-calculus, reducing some query y | do(x) see(w) to only observation
    """

    def __init__(self, graph: Graph, y, x, w):
        """
        Create an iterative-deepening-search solver to manipulate the given sets until there are no interventions left.
        :param graph: A Graph object representing the graph space
        :param y: The outcomes we wish to measure, as a set of strings
        :param x: All interventions, as a set of strings
        :param w: All observations, as a set of strings
        """
        self.graph = graph.copy()
        self.y = y
        self.x = x
        self.w = w

        self.stack = Stack()

    def solve(self) -> Solution:
        """
        Solve The given problem
        :return:
        """

        maximum_depth = 10
        current_max_depth = 1

        while current_max_depth <= maximum_depth:

            self.stack.clear()
            self.stack.push((self.graph.copy(), self.y.copy(), self.x.copy(), self.w.copy(), 1))

            while not self.stack.empty():

                # Pop the current item in the IDS stack and see if it's our goal
                current = self.stack.pop()
                if self.goal(current):
                    return Solution(True, current)

                # Unpack the item and see if we can push all its resulting options
                current_graph, current_y, current_x, current_w, item_depth = current
                if item_depth < current_max_depth:

                    # Generate all new options
                    all_options = do_calculus_options(current_graph.copy(), current_y, current_x, current_w)
                    for option in all_options:
                        new_y, new_x, new_w = option[0].data
                        self.stack.push((current_graph.copy(), new_y, new_x, new_w, item_depth+1))

        return Solution(False, None)

    def goal(self, x: tuple):
        return len(x) == 0
