from pyflowlauncher import Result, handle_response
from pyflowlauncher.result import send_results


def test_none():
    assert handle_response(None) is None


def test_single_result():
    r = Result(title="hello")
    assert handle_response(r) == send_results([r])


def test_list_of_results():
    results = [Result(title="a"), Result(title="b")]
    assert handle_response(results) == send_results(results)


def test_generator_single_result():
    def gen():
        yield Result(title="a")

    assert handle_response(gen()) == send_results([Result(title="a")])


def test_generator_multiple_results():
    def gen():
        yield Result(title="a")
        yield Result(title="b")

    assert handle_response(gen()) == send_results([Result(title="a"), Result(title="b")])


def test_generator_yields_list():
    def gen():
        yield [Result(title="a"), Result(title="b")]

    assert handle_response(gen()) == send_results([Result(title="a"), Result(title="b")])


def test_generator_mixed_yields():
    def gen():
        yield Result(title="a")
        yield [Result(title="b"), Result(title="c")]

    assert handle_response(gen()) == send_results([
        Result(title="a"), Result(title="b"), Result(title="c")
    ])


def test_jsonrpc_request_passthrough():
    req = {"Method": "Flow.Launcher.HideApp", "Parameters": []}
    assert handle_response(req) is req


def test_jsonrpc_response_passthrough():
    resp = send_results([Result(title="x")])
    assert handle_response(resp) is resp


def test_list_with_non_result_items_filtered():
    results = [Result(title="a"), "not a result", 42]
    assert handle_response(results) == send_results([Result(title="a")])
