from .core.API import API as Core
from .deconfounding.API import API as Deconfounding


class API(Core, Deconfounding):

    def __init__(self) -> None:
        Core.__init__(self)
        Deconfounding.__init__(self)
