from .core.API import Core_API
from .deconfounding.API import Deconfounding_API

class API(Core_API, Deconfounding_API):

    ...


x = API()

x.foo()
x.bar()
