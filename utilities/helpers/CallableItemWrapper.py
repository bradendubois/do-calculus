#########################################################
#                                                       #
#   PowerSet                                            #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################


class CallableItemWrapper:
    """Helper class to allow data to be passed through my menu / io system without errors by being "callable" """

    def __init__(self, *data):
        self.data = data

    # My menu system has behaviour defined by "callable" data, so this is a bit of a workaround.
    def __call__(self, *args, **kwargs):
        pass
