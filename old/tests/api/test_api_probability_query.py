from do.api.probability_query import api_probability_query_parse, api_probability_query
from do.structures.VariableStructures import Outcome, Intervention

from ..test_driver import cg


def test_api_probability_query():

    x = Outcome("X", "x")
    y = Outcome("Y", "y")
    z = Outcome("Z", "z")

    v = Intervention("V", "v")
    w = Intervention("W", "w")

    head_and_body = "Y=y, X=x | Z=z, do(W=w, V=v)"
    head_only = "Y=y, X=x"
    single_both = "Y=y | X = x"
    single_head = "Y = y"

    assert api_probability_query_parse(head_and_body) == {"y": {y, x}, "x": {z, w, v}}
    assert api_probability_query_parse(head_only) == {"y": {y, x}, "x": set()}
    assert api_probability_query_parse(single_both) == {"y": {y}, "x": {x}}
    assert api_probability_query_parse(single_head) == {"y": {y}, "x": set()}

    xi = Outcome("Xi", "xi")
    xj = Outcome("Xj", "xj")
    assert api_probability_query(cg, {xj}, {xi}) == cg.probability_query({xj}, {xi})
