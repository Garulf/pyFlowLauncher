from pyflowlauncher.method import Method
from pyflowlauncher.result import Result


def test_add_results():
    class TestMethod(Method):
        def __call__(self, *args, **kwargs):
            result = Result("title", "subtitle", "icon.png")
            self.add_result(result)

    method = TestMethod()
    method()
    assert method._results == [Result("title", "subtitle", "icon.png")]


def test_return_results():
    result = Result("title", "subtitle", "icon.png")

    class TestMethod(Method):
        def __call__(self, *args, **kwargs):
            self.add_result(result)
            return self.return_results()

    method = TestMethod()
    assert method() == {"result": [result.as_dict()], 'SettingsChange': None}
