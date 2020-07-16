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

from do_calculus.application.QueryStructures import QueryList, Query, QueryBody
from do_calculus.application.DoCalculusQueryOptions import do_calculus_options
from do_calculus.ids_ai.Stack import Stack
from probability_structures.Graph import Graph


class Solution:
    """Wrapper to represent the results of the IDS Searcher"""

    def __init__(self, success: bool, history=None, result=None):
        """
        A basic "Solution" object initializer
        :param success: A True/False representing success in finding a solution
        :param history: A list, the history/steps taken to reach the final result
        :param result: The item/data result itself, should be a proper QueryList reduced to no interventions
        """
        self.success = success
        self.history = history
        self.result = result

    def __str__(self) -> str:
        """
        Basic string builtin for the Solution
        :return: A String representation of the Solution,
        """
        msg = ""
        msg += str(self.success) + "\n"
        if self.success:
            msg += "\n".join(str(i) for i in self.history) + "\n"
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

        # We will go to a depth maximum 10, starting with 1, and increasing until we find it.
        maximum_depth = 10
        current_max_depth = 1

        while current_max_depth <= maximum_depth:

            # Watch the exponential growth explode in real time.
            # print(current_max_depth)

            # Clear the stack and push our "starter" data
            self.stack.clear()
            self.stack.push((QueryList([Query(self.y.copy(), QueryBody(self.x.copy(), self.w.copy()))]), 1, []))

            while not self.stack.empty():

                # Pop the current item in the IDS stack and see if it's our goal
                current, item_depth, history = self.stack.pop()
                if self.goal(current):
                    return Solution(True, history, current)

                # Unpack the item and see if we can push all its resulting options
                if item_depth < current_max_depth:

                    # Generate all new options
                    all_options = do_calculus_options(current, self.graph)

                    # Push each option
                    for option in all_options:

                        # As unpacked above, this is a tuple (query state, depth, history)
                        self.stack.push((option[1], item_depth+1, history + [option[0]]))

            # Increase the depth and run again
            current_max_depth += 1

        # No Solution found
        return Solution(False)

    def goal(self, x: QueryList) -> bool:
        """
        Determine whether or not a given QueryList is a "goal"; it would simply be that the QueryList
        is fully resolved, and no longer contains any "do" operators.
        :param x: A QueryList to check
        :return: True if this QueryList is a valid Goal, False otherwise
        """
        return x.no_interventions()
