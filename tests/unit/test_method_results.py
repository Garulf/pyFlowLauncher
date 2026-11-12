from pyflowlauncher.method import Method
from pyflowlauncher.result import Result


class Echo(Method):
    def __call__(self, query):
        self.add_result(Result(title=query))
        return self.return_results()


def titles(response):
    return [item["Title"] for item in response["Result"]]


def test_results_do_not_carry_over_between_calls():
    method = Echo()

    assert titles(method("a")) == ["a"]
    assert titles(method("b")) == ["b"]
    assert titles(method("c")) == ["c"]


def test_return_results_empties_the_list():
    method = Echo()
    method("a")

    assert method._results == []


def test_return_results_passes_settings_through():
    method = Echo()
    method.add_result(Result(title="a"))

    response = method.return_results({"key": "value"})

    assert response["SettingsChange"] == {"key": "value"}
    assert titles(response) == ["a"]
