#########################################################
#                                                       #
#   Query Structures                                    #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# A way of representing a list of queries to be multiplied together, some of which may involve Summations


class Sigma:
    """Basic "Sigma" representation"""

    def __init__(self, over: set):
        """
        Initializer for a Sigma object
        :param over: The set of all variables (strings) the following information should be conditioned over
        """
        self.over = over

    def __str__(self) -> str:
        """
        String builtin for the Sigma class
        :return: String representation of a Sigma instance
        """
        return "Sigma_" + ",".join(sorted(i for i in self.over))

    def __copy__(self):
        """
        Copy builtin for the Sigma class
        :return: A copy of the given Sigma instance
        """
        return Sigma(self.over.copy())

    def copy(self):
        """
        Exposed Copy method for the Sigma class
        :return: A copy of the given Sigma instance
        """
        return self.__copy__()


class QueryBody:
    """Basic way of representing the body of a query, differentiating between interventions and observations"""

    def __init__(self, interventions: set, observations: set):
        """
        Initializer for the QueryBody class
        :param interventions: A set of strings, representing the variables this query is "doing" as interventions
        :param observations: A set of strings, representing the variables this query is "seeing" as observations
        """
        self.interventions = interventions
        self.observations = observations

    def __str__(self) -> str:
        """
        String builtin for the QueryBody class
        :return: A string representation of the given QueryBody instance
        """
        msg = ""
        if len(self.interventions) > 0:
            msg += "do(" + ", ".join(sorted(i for i in self.interventions)) + ")"
        if len(self.interventions) > 0 and len(self.observations) > 0:
            msg += ", "
        if len(self.observations) > 0:
            msg += ", ".join(sorted(i for i in self.observations))
        return msg

    def __copy__(self):
        """
        Copy builtin for the QueryBody class
        :return: A copy of the given QueryBody instance
        """
        return QueryBody(self.interventions.copy(), self.observations.copy())

    def copy(self):
        """
        Exposed copy method for the QueryBody class
        :return: A copy of the given QueryBody instance
        """
        return self.__copy__()


class Query:
    """A basic Query, which may contain do-operations"""

    def __init__(self, head: set, body: QueryBody):
        """
        Initializer for a basic Query
        :param head: A set of strings, each representing a variable
        :param body: A QueryBody object, holding the observations and interventions
        """
        self.head = head
        self.body = body

    def __str__(self) -> str:
        """
        String builtin for the Query class
        :return: A string representation of the given Query instance
        """
        msg = "P(" + ", ".join(sorted(i for i in self.head))
        if len(self.body.interventions | self.body.observations) > 0:
            msg += " | " + str(self.body)
        return msg + ")"

    def __hash__(self) -> int:
        """
        Hash builtin for the Query class
        :return: A hash representation of the given Query instance
        """
        return hash(",".join(list(self.head | self.body.interventions | self.body.observations)))

    def __copy__(self):
        """
        Copy builtin for the Query class
        :return: A copy of the given Query instance
        """
        return Query(self.head.copy(), self.body.copy())

    def copy(self):
        """
        Exposed copy method for the Query class
        :return: A copy of the given Query instance
        """
        return self.__copy__()

    def resolved(self) -> bool:
        """
        Determine whether this Query is "resolved", which means it contains no intervention variables.
        :return: True if there are no interventions, False otherwise.
        """
        return len(self.body.interventions) == 0


class QueryList:
    """A container class representing any number of Sigma/Query objects"""

    def __init__(self, queries: list):
        """
        Initializer for a QueryList instance
        :param queries: A list any number of Sigma/Query objects
        """
        self.queries = queries

    def __str__(self) -> str:
        """
        String builtin for the QueryList class
        :return: A string representation of the given QueryList instance
        """
        return " ".join(str(item) for item in self.queries)

    def __copy__(self):
        """
        Copy builtin for the QueryList class
        :return: A copy of the given QueryList instance
        """
        return QueryList([query.copy() for query in self.queries])

    def copy(self):
        """
        Exposed copy method for the QueryList class
        :return: A copy of the given QueryList instance
        """
        return self.__copy__()

    def no_interventions(self) -> bool:
        """
        Check whether the given list of queries contains no interventions in any Query
        :return: True if there are no interventions, False otherwise
        """
        for item in self.queries:
            if isinstance(item, Query) and not item.resolved():
                return False
        return True
