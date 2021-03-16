#########################################################
#                                                       #
#   IDS Solver                                          #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Basic IDS-approach solver taking an initial query and solving until there are no interventions left
#   Thanks, Professor Horsch, for CMPT 317!

from src.probability.do_calculus.application.CustomSetFunctions import clean
from src.probability.do_calculus.application.QueryStructures import QueryList, Query, QueryBody
from src.probability.do_calculus.application.DoCalculusQueryOptions import do_calculus_options, query_cache
from src.probability.do_calculus.ids_ai.Stack import Stack
from src.probability.do_calculus.ids_ai.Solution import Solution
from src.probability.structures.Graph import Graph
from src.util.Decorators import print_time


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
        self.u = u if u else set()

        self.initial_query_list = QueryList([Query(self.y.copy(), QueryBody(self.x.copy(), self.w.copy()))])

        self.stack = Stack()

    @print_time
    def solve(self) -> Solution:
        """
        Solve The given problem
        :return: A Solution object either indicating failure or a resolved QueryList object
        """

        # Used to prevent wasteful / unfruitful paths to go down; especially useful with depth increase
        seen = set()

        # When a specific query of some sort is seen, cache all the options available to it rather than re-generate
        #   them all from scratch; this cache will be the total QueryList object, not each respective query
        cached = dict()

        # Reset the cache when beginning a search in case we've switched files
        query_cache.clear()

        # We will go to a depth maximum 100, starting with 1, and increasing until we find it.
        maximum_depth = 100
        current_max_depth = 1

        while current_max_depth <= maximum_depth:

            # Watch the exponential growth explode in real time.
            # print(current_max_depth)

            # Clear the stack and push our "starter" data
            self.stack.clear()
            self.stack.push((self.initial_query_list.copy(), 1, []))

            # Clear the "seen" for this depth
            seen.clear()

            unexplored = True

            while not self.stack.empty():

                # Pop the current item in the IDS stack and see if it's our goal
                current, item_depth, history = self.stack.pop()
                if self.goal(current):
                    return Solution(True, history, current)

                # String representation so as to not repeat an unnecessary path
                str_rep = str(current)

                # Unpack the item and see if we can push all its resulting options
                if item_depth < current_max_depth and str_rep not in seen:

                    # Add the string to ensure we don't compute all this again for an equivalent query
                    seen.add(str_rep)

                    # Don't generate any new options if there is an unobservable variable introduced
                    if self.contains_unobservable(current):
                        continue

                    # Already generated these results
                    if str_rep in cached:
                        all_options = cached[str_rep]

                    # Generate all new options
                    else:
                        all_options = do_calculus_options(current, self.graph, self.u)
                        if item_depth < 5:
                            cached[str_rep] = all_options

                    # Push each option
                    for option in all_options:

                        # As unpacked above, this is a tuple (query state, depth, history)
                        self.stack.push((option[1], item_depth+1, history + [option[0]]))

                elif item_depth >= current_max_depth:
                    unexplored = True

            # Couldn't find an answer at this depth
            # io.write_log("Couldn't find a solution at depth:", current_max_depth, "Looked at:", len(seen), "queries.")

            # The stack was fully exhausted, but never through a depth-limit; we have no more options to explore
            if not unexplored:
                # io.write_log("There are no more branches to explore; the solver cannot find an answer.")
                break

            # Increase the depth and run again
            current_max_depth += 1

        # No Solution found
        return Solution(False)

    def contains_unobservable(self, x: QueryList) -> bool:
        """
        Determine whether a given QueryList object contains any unobservable variables, which would be considered
        unacceptable in a solution returned by the IDS search.
        :param x: A QueryList object
        :return: True if there are any unobservable
        """
        for item in x.queries:
            if isinstance(item, Query):
                if len((item.head | item.body.interventions | item.body.observations) & self.u) != 0:
                    return True
        return False

    def goal(self, x: QueryList) -> bool:
        """
        Determine whether or not a given QueryList is a "goal"; it would simply be that the QueryList
        is fully resolved, and no longer contains any "do" operators.
        :param x: A QueryList to check
        :return: True if this QueryList is a valid Goal, False otherwise
        """
        # Ensure that any unobservable variables are not used in the final solution
        for query in x.queries:                 # Check each query
            if isinstance(query, Query):        # Filter out Sigma's
                if not query.resolved():
                    return False

                all_used = clean(query.head) | clean(query.body.interventions) | clean(query.body.observations)
                if len(all_used & self.u) != 0:
                    return False

        return True
