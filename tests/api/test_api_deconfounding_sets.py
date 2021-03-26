from do.api.deconfounding_sets import api_deconfounding_sets_parse, api_deconfounding_sets

from ..test_driver import bc


def test_api_deconfounding_sets():

    paths = ({"Xi"}, {"Xj"})
    paths2 = ({"Xj"}, {"Xi"})
    no_paths = ({"X1"}, {"Xj"})

    unfixable = ({"Xi", "X4", "X2"}, {"Xj"})

    assert api_deconfounding_sets_parse("Xi, X1 -> Xj") == {"src": {"Xi", "X1"}, "dst": {"Xj"}}
    assert api_deconfounding_sets_parse("Xi -> Xj") == {"src": {"Xi"}, "dst": {"Xj"}}
    assert api_deconfounding_sets_parse("Xj -> Xi") == {"src": {"Xj"}, "dst": {"Xi"}}
    assert api_deconfounding_sets_parse("X1 -> Xj") == {"src": {"X1"}, "dst": {"Xj"}}
    assert api_deconfounding_sets_parse("Xi, X4, X2 -> Xj") == {"src": {"Xi", "X4", "X2"}, "dst": {"Xj"}}

    assert len(api_deconfounding_sets(bc, *paths)) > 0
    assert len(api_deconfounding_sets(bc, *paths2)) > 0
    assert len(api_deconfounding_sets(bc, *no_paths)) > 0
    assert len(api_deconfounding_sets(bc, *unfixable)) == 0

    assert api_deconfounding_sets(bc, *paths) == bc.all_dcf_sets(*paths)
    assert api_deconfounding_sets(bc, *paths2) == bc.all_dcf_sets(*paths2)
    assert api_deconfounding_sets(bc, *no_paths) == bc.all_dcf_sets(*no_paths)
    assert api_deconfounding_sets(bc, *unfixable) == bc.all_dcf_sets(*unfixable)
