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
from probability_structures.do_calculus.application.CustomSetFunctions import clean
from probability_structures.do_calculus.application.QueryStructures import QueryList, Query, QueryBody
from probability_structures.do_calculus.application.DoCalculusQueryOptions import do_calculus_options
from probability_structures.do_calculus.ids_ai.Stack import Stack
from probability_structures.Graph import Graph
from util.IO_Logger import io


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

    def __init__(self, graph: Graph, y: set, x: set, w: set, u=None):
        """
        Create an iterative-deepening-search solver to manipulate the given sets until there are no interventions left.
        :param graph: A Graph object representing the graph space
        :param y: The outcomes we wish to measure, as a set of strings
        :param x: All interventions, as a set of strings
        :param w: All observations, as a set of strings
        :param u: All unobservable variables, as a set of strings
        """
        self.graph = graph.copy()
        self.y = y
        self.x = x
        self.w = w

        # Either store u, or create an empty set
        self.unobservable = u if u else set()

        self.initial_query_list = QueryList([Query(self.y.copy(), QueryBody(self.x.copy(), self.w.copy()))])

        self.stack = Stack()

    def solve(self) -> Solution:
        """
        Solve The given problem
        :return:
        """

        # Used to prevent wasteful / unfruitful paths to go down; especially useful with depth increase
        seen = set()

        # We will go to a depth maximum 10, starting with 1, and increasing until we find it.
        maximum_depth = 10
        current_max_depth = 1

        # Test to see how many queries are actually caught by the "seen" set
        t = 0

        while current_max_depth <= maximum_depth:

            # Watch the exponential growth explode in real time.
            # print(current_max_depth)

            # Clear the stack and push our "starter" data
            self.stack.clear()
            self.stack.push((self.initial_query_list.copy(), 1, []))

            # Clear the "seen"
            seen.clear()

            while not self.stack.empty():

                # Pop the current item in the IDS stack and see if it's our goal
                current, item_depth, history = self.stack.pop()
                if self.goal(current):
                    print("Bounced", str(t), "duplicate states.")
                    return Solution(True, history, current)

                # String representation so as to not repeat an unnecessary path
                str_rep = str(current)

                if str_rep in seen:
                    t += 1

                # Unpack the item and see if we can push all its resulting options
                if item_depth < current_max_depth and str_rep not in seen:

                    # Add the string to ensure we don't compute all this again for an equivalent query
                    seen.add(str_rep)

                    # Generate all new options
                    all_options = do_calculus_options(current, self.graph)

                    # Push each option
                    for option in all_options:

                        # As unpacked above, this is a tuple (query state, depth, history)
                        self.stack.push((option[1], item_depth+1, history + [option[0]]))

            # Couldn't find an answer at this depth
            io.write("Couldn't find a solution at depth:", current_max_depth, "Looked at:", len(seen), "queries.")

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
        # Ensure there are no more "do's"
        if not x.no_interventions():
            return False

        # Ensure that any unobservable variables are not used in the final solution
        for query in x.queries:                 # Check each query
            if isinstance(query, Query):        # Filter out Sigma's
                all_used = clean(query.head) | clean(query.body.interventions) | clean(query.body.observations)
                if len(all_used & self.unobservable) != 0:
                    return False

        return True
