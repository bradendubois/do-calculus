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

from do_calculus.QueryList import QueryList, Query, VariableSet
from do_calculus.application.DoCalculusOptionsRevised import do_calculus_options
from do_calculus.ids_ai.Stack import Stack
from probability_structures.Graph import Graph


class Solution:
    """Wrapper to represent the results of the IDS Searcher"""

    def __init__(self, success: bool, history, result):
        self.success = success
        self.history = history
        self.result = result

    def __str__(self):
        msg = ""
        msg += str(self.success) + "\n"
        if self.success:
            for item in self.history:
                msg += ".....".join(str(i) for i in item) + "\n"
            msg += str(self.result)
        return msg


class IDSSolver:
    """
    A basic iterative-deepening-search approach to do-calculus, reducing some query y | do(x) see(w) to only observation
    """

    def __init__(self, graph: Graph, y: set, x: set, w: set):
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

            # Watch the exponential growth explode in real time.
            # print(current_max_depth)

            # Clear the stack and push our "starter" data
            self.stack.clear()
            self.stack.push((QueryList([Query(self.y.copy(), VariableSet(self.x.copy(), self.w.copy()))]), 1, []))

            while not self.stack.empty():

                # Pop the current item in the IDS stack and see if it's our goal
                current, item_depth, history = self.stack.pop()
                if self.goal(current):
                    return Solution(True, history, current)

                # Unpack the item and see if we can push all its resulting options
                if item_depth < current_max_depth:

                    # Generate all new options
                    all_options = do_calculus_options(current, self.graph)
                    for option in all_options:
                        self.stack.push((option[1], item_depth+1, history + [(option[0], current)]))

            current_max_depth += 1

        return Solution(False, None)

    def goal(self, x: QueryList):
        return x.fully_resolved()
