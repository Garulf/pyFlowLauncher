import pytest
from pyflowlauncher import Plugin, Result, handle_response
from pyflowlauncher.result import send_results


# --- Unit tests for handle_response ---

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


# --- Integration: @plugin.on_method with generator ---

def test_on_method_generator_integration():
    plugin = Plugin()

    @plugin.on_method
    def query(q: str):
        yield Result(title="foo")
        yield Result(title="bar")

    import asyncio
    result = asyncio.run(plugin._event_handler.trigger_event("query", "test"))
    assert result == send_results([Result(title="foo"), Result(title="bar")])


def test_on_method_single_result_integration():
    plugin = Plugin()

    @plugin.on_method
    def query(q: str):
        return Result(title="only")

    import asyncio
    result = asyncio.run(plugin._event_handler.trigger_event("query", "test"))
    assert result == send_results([Result(title="only")])


def test_on_method_list_integration():
    plugin = Plugin()

    @plugin.on_method
    def query(q: str):
        return [Result(title="a"), Result(title="b")]

    import asyncio
    result = asyncio.run(plugin._event_handler.trigger_event("query", "test"))
    assert result == send_results([Result(title="a"), Result(title="b")])


# --- Async generator support ---

@pytest.mark.asyncio
async def test_async_generator_single():
    plugin = Plugin()

    @plugin.on_method
    async def query(q: str):
        yield Result(title="async-foo")

    result = await plugin._event_handler.trigger_event("query", "test")
    assert result == send_results([Result(title="async-foo")])


@pytest.mark.asyncio
async def test_async_generator_multiple():
    plugin = Plugin()

    @plugin.on_method
    async def query(q: str):
        yield Result(title="a")
        yield Result(title="b")

    result = await plugin._event_handler.trigger_event("query", "test")
    assert result == send_results([Result(title="a"), Result(title="b")])


@pytest.mark.asyncio
async def test_async_generator_yields_list():
    plugin = Plugin()

    @plugin.on_method
    async def query(q: str):
        yield [Result(title="x"), Result(title="y")]

    result = await plugin._event_handler.trigger_event("query", "test")
    assert result == send_results([Result(title="x"), Result(title="y")])


# --- Regression: _is_registered_method on on_method return value ---

def test_on_method_result_has_registered_flag():
    plugin = Plugin()

    @plugin.on_method
    def query(q: str):
        return Result(title="x")

    assert getattr(query, '_is_registered_method', False) is True


def test_add_method_result_has_registered_flag():
    plugin = Plugin()

    def query(q: str):
        return Result(title="x")

    plugin.add_method(query)
    assert getattr(query, '_is_registered_method', False) is True


def test_on_method_add_action_does_not_raise():
    plugin = Plugin()

    @plugin.on_method
    def action_handler():
        pass

    r = Result(title="x")
    r.add_action(action_handler)  # should not raise MethodNotRegisteredError


# --- Regression: async def returning Result/list ---

@pytest.mark.asyncio
async def test_async_return_single_result():
    plugin = Plugin()

    @plugin.on_method
    async def query(q: str):
        return Result(title="async-return")

    result = await plugin._event_handler.trigger_event("query", "test")
    assert result == send_results([Result(title="async-return")])


@pytest.mark.asyncio
async def test_async_return_list_of_results():
    plugin = Plugin()

    @plugin.on_method
    async def query(q: str):
        return [Result(title="a"), Result(title="b")]

    result = await plugin._event_handler.trigger_event("query", "test")
    assert result == send_results([Result(title="a"), Result(title="b")])


# --- Regression: list branch filters non-Result items ---

def test_list_with_non_result_items_filtered():
    results = [Result(title="a"), "not a result", 42]
    assert handle_response(results) == send_results([Result(title="a")])
