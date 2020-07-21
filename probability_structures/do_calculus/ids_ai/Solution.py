#########################################################
#                                                       #
#   Solution                                            #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# A basic Solution class / abstraction for the IDS Solver


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
