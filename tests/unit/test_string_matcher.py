import pyflowlauncher.string_matcher as string_matcher


def test_exact_match():
    match_data = string_matcher.MatchData(
        True,
        50,
        [0, 1, 2, 3],
        143
    )
    assert string_matcher.string_matcher("test", "test") == match_data


def test_bad_match():
    match_data = string_matcher.MatchData(
        False,
        50,
        [],
        0
    )
    assert string_matcher.string_matcher("foo", "bar") == match_data


def test_ignore_case():
    match_data = string_matcher.MatchData(
        True,
        50,
        [0, 1, 2, 3],
        143
    )
    assert string_matcher.string_matcher("test", "Test", ignore_case=True) == match_data


def test_ignore_case_false():
    match_data = string_matcher.MatchData(
        False,
        50,
        [],
        0
    )
    assert string_matcher.string_matcher("test", "Test", ignore_case=False) == match_data


def test_ignore_case_false_acronym():
    match_data = string_matcher.MatchData(
        False,
        50,
        [],
        0
    )
    assert string_matcher.string_matcher("fb", "Foo Bar", ignore_case=False, query_search_precision=50) == match_data


def test_ignore_case_true_acronym():
    match_data = string_matcher.MatchData(
        matched=True,
        score_cutoff=50,
        index_list=[0, 4],
        score=100
    )
    assert string_matcher.string_matcher("fb", "Foo Bar", ignore_case=True, query_search_precision=50) == match_data


def test_subtext():
    match_data = string_matcher.MatchData(
        matched=True,
        score_cutoff=50,
        index_list=[4, 5, 6],
        score=119
    )
    assert string_matcher.string_matcher("bar", "foo bar baz", query_search_precision=50) == match_data