import pytest

from pyflowlauncher.method import Method
from pyflowlauncher.result import Result


class Echo(Method):
    def __call__(self, query):
        self.add_result(Result(title=query))
        return self.return_results()


def make_echo():
    with pytest.warns(DeprecationWarning):
        return Echo()


def titles(response):
    return [item["Title"] for item in response["Result"]]


def test_results_do_not_carry_over_between_calls():
    method = make_echo()

    assert titles(method("a")) == ["a"]
    assert titles(method("b")) == ["b"]
    assert titles(method("c")) == ["c"]


def test_return_results_empties_the_list():
    method = make_echo()
    method("a")

    assert method._results == []


def test_return_results_passes_settings_through():
    method = make_echo()
    method.add_result(Result(title="a"))

    response = method.return_results({"key": "value"})

    assert response["SettingsChange"] == {"key": "value"}
    assert titles(response) == ["a"]
