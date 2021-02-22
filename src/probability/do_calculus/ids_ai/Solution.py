#########################################################
#                                                       #
#   Solution                                            #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# A basic Solution class / abstraction for the IDS Solver

from src.probability.do_calculus.application.QueryStructures import QueryList, Sigma, Query


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
        self.result = reorder(result)

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


def reorder(ql: QueryList) -> QueryList:

    reordered = []

    # Separate the query into its Query and Sigma objects
    items = [q for q in ql.queries if isinstance(q, Query)]
    sigmas = [s for s in ql.queries if isinstance(s, Sigma)]

    # Go right-to-left to preserve the correct order
    for sigma in sigmas[::-1]:

        # Drop anything "here" that uses the current Sigma object, and push it to the front of the re-ordered list
        drop = [q for q in items if len(full_v_union(q) & sigma.over) != 0]
        reordered = [sigma, *drop] + reordered
        items = [i for i in items if i not in drop]

    # Return a new QueryList object that has any "remaining" Query items that don't need use any Sigma objects at front
    return QueryList(list(items) + reordered)


def full_v_union(q: Query):
    return q.head | q.body.interventions | q.body.observations
