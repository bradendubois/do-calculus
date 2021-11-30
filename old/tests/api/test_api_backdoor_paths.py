from do.api.backdoor_paths import api_backdoor_paths_parse, api_backdoor_paths

from ..test_driver import bc


def test_api_backdoor_paths():

    blocked = ({"Xi"}, {"Xj"}, {"X4", "X2"})
    unblocked = ({"Xi"}, {"Xj"}, set())

    assert api_backdoor_paths_parse("Xi -> Xj") == {"src": {"Xi"}, "dst": {"Xj"}, "dcf": set()}
    assert api_backdoor_paths_parse("Xi -> Xj | X4, X2") == {"src": {"Xi"}, "dst": {"Xj"}, "dcf": {"X4", "X2"}}

    assert len(api_backdoor_paths(bc, *unblocked)) > 0
    assert len(api_backdoor_paths(bc, *blocked)) == 0

    assert api_backdoor_paths(bc, *unblocked) == bc.backdoor_paths(*unblocked)
    assert api_backdoor_paths(bc, *blocked) == bc.backdoor_paths(*blocked)
