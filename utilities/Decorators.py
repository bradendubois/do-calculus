#########################################################
#                                                       #
#   Decorators.py                                       #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# A collection of decorators that can make debugging / changes / new features easier

from datetime import datetime
import functools


def time(function):
    """
    Helper function to time a function (used for debug purposes)
    :param function: The function to time
    :return: The time (in seconds) taken to run function
    """

    @functools.wraps(function)
    def time_function(*args, **kwargs):

        start_time = datetime.now()     # Take current time
        function(*args, **kwargs)
        end_time = datetime.now()       # Take new current time
        taken = end_time - start_time   # Take the difference
        # print(function.__name__ + " completed in: " + str(taken) + " seconds.")
        return taken

    return time_function


def debug(function):
    """
    Debug a function by showing everything it was provided, returns, etc.
    :param function: The function to run
    """

    @functools.wraps(function)
    def wrapper_debug(*args, **kwargs):
        str_args = ", ".join([str(a) for a in args])
        str_kwargs = ",".join(["{}={}".format(k, v) for k, v in kwargs.items()])
        result = function(*args, **kwargs)
        print("{} called with {}, {}, returned {}".format(function.__name__, str_args, str_kwargs, result))
        return result

    return wrapper_debug
