from .core.API import API as Core
from .deconfounding.API import API as Deconfounding

apis = [Core, Deconfounding]

class API(*apis):

    ...
