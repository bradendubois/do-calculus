#########################################################
#                                                       #
#   Result Cache                                        #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Store a result, mapped to by some string representation of its query

from src.config.config_manager import access

# Just use some dictionary to map
stored_computations = dict()


def store_computation(string_representation: str, result: float or (float, float)):
    """
    Store a computed result mapped by its query/representation, to speed up future queries
    :param string_representation: Whatever representation for this query: "P(Y | X)", etc.
    :param result: The actual value to store, float for probabilities, (float, float) for continuous
    """
    # Ensure the configuration file is specified to allow caching
    if access("cache_computation_results"):

        # Not stored yet - store it
        if string_representation not in stored_computations:
            stored_computations[string_representation] = result

        # Stored already but with a different value - something fishy is going on...
        elif stored_computations[string_representation] != result:
            print("Uh-oh:", string_representation, "has already been cached, but with a different value...")
