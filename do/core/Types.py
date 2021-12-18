from typing import Sequence, Union

from .Variables import Variable, Outcome, Intervention

# Variable-related

VClass = Union[Variable, Outcome, Intervention]
"""
A VClass is any of a Variable, Outcome, or Intervention.

Usage of VClass for type-hinting is useful when the variable need not have
a known value / measurement. For example, VClass might be used in graph-related
components in which the 'name' of the variable is the important feature, whether
the variable be provided as any of the Variable, Outcome, or Intervention class types.
"""


VMeasured = Union[Outcome, Intervention]
"""
A VMeasured is either of an Outcome or Intervention.

Usage of VMeasured is useful in querying distributions on a model; a variable on its
own does not indicate much, but a discrete value represents a measurement/observation (Outcome)
or a treatment (Intervention).
"""


# Graph-related

Vertex = Union[VClass, str]
"""
A Vertex is any of a Variable, Outcome, Intervention, or string.

It may happen that one has any of (or any combination of) the above, and some path-finding
must be done. The Graph class itself stores only strings as vertices, and we can treat
a string as the name of vertex, or the 'name' field of any of the Variable, Outcome, or Intervention
as corresponding to a named vertex.
"""


Path = Sequence[str]
"""
A Path may be yielded in deconfounding (see: Backdoor/Frontdoor Criterions) and is represented
as a sequence of string vertex labels.
"""
