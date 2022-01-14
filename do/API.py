from .core.API import API as Core
from .deconfounding.API import API as Deconfounding
from .identification.API import API as Identification

class API(Core, Deconfounding, Identification):

    def __init__(self):
        Core.__init__(self)
        Deconfounding.__init__(self)
        Identification.__init__(self)
