import pytest

import pyflowlauncher
from pyflowlauncher import Plugin, Result
from pyflowlauncher.method import Method


class Query(Method):
    def __call__(self, query):
        self.add_result(Result(title=query))
        return self.return_results()


class QueryWithInit(Query):
    def __init__(self):
        super().__init__()


def test_constructing_a_method_warns():
    with pytest.warns(DeprecationWarning, match="on_method"):
        Query()


def test_warning_points_at_the_constructing_code():
    with pytest.warns(DeprecationWarning) as record:
        Query()

    assert record[0].filename == __file__


def test_warning_points_at_the_constructing_code_when_init_is_overridden():
    with pytest.warns(DeprecationWarning) as record:
        QueryWithInit()

    assert record[0].filename == __file__


def test_method_is_still_exported():
    assert pyflowlauncher.Method is Method


def test_method_still_works_when_registered_by_name():
    plugin = Plugin()
    with pytest.warns(DeprecationWarning):
        instance = Query()

    plugin.add_method(instance, name="query")
    handler = plugin._event_handler.get_event("query")

    assert [r["Title"] for r in handler("a")["Result"]] == ["a"]
    assert [r["Title"] for r in handler("b")["Result"]] == ["b"]
