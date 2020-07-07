#########################################################
#                                                       #
#   IterableIndexSelection                              #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Reducing some code copying; if I have some iterable set, and I want to get a selection
#   of one element of it from the user, this will generate said menu and get a valid selection


def user_index_selection(header: str, items: list) -> int:
    """
    Take some list of items, query the user to select one of them.
    :param header: The header/top of the message.
    :param items: The list of items; in the case of function/callback selection, the item would be a
        list itself, the first being the function, the second being a string representation
    :return: A valid index in the the list items
    """

    # Actually print the menu, constructed from "options"
    print("\n" + header)
    for i in range(len(items)):
        if isinstance(items[i], list):
            representation = items[i][1]
        else:
            representation = items[i]
        print("  " + str(i+1) + ") " + str(representation))

    # Repeatedly re-query until a valid selection is made
    selection = input("\n  Query: ")
    while not selection.isdigit() or not 1 <= int(selection) <= len(items):
        print("*** Invalid Selection ***")
        selection = input("  Query: ")

    return int(selection)-1
