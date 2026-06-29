"""
Integration tests for Plugin method registration and dispatch.

Tests the full chain: @plugin.on_method decorator → EventHandler → handle_response,
covering sync generators, async generators, and return styles.
"""

import asyncio

import pytest

from pyflowlauncher import Plugin, Result
from pyflowlauncher.result import send_results


# ---------------------------------------------------------------------------
# Sync generators / returns
# ---------------------------------------------------------------------------

def test_on_method_yields_results():
    plugin = Plugin()

    @plugin.on_method
    def query(q: str):
        yield Result(title="foo")
        yield Result(title="bar")

    result = asyncio.run(plugin._event_handler.trigger_event("query", "test"))
    assert result == send_results([Result(title="foo"), Result(title="bar")])


def test_on_method_returns_single_result():
    plugin = Plugin()

    @plugin.on_method
    def query(q: str):
        return Result(title="only")

    result = asyncio.run(plugin._event_handler.trigger_event("query", "test"))
    assert result == send_results([Result(title="only")])


def test_on_method_returns_list():
    plugin = Plugin()

    @plugin.on_method
    def query(q: str):
        return [Result(title="a"), Result(title="b")]

    result = asyncio.run(plugin._event_handler.trigger_event("query", "test"))
    assert result == send_results([Result(title="a"), Result(title="b")])


# ---------------------------------------------------------------------------
# Async generators / returns
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Method registration
# ---------------------------------------------------------------------------

def test_on_method_sets_registered_flag():
    plugin = Plugin()

    @plugin.on_method
    def query(q: str):
        return Result(title="x")

    assert getattr(query, '_is_registered_method', False) is True


def test_add_method_sets_registered_flag():
    plugin = Plugin()

    def query(q: str):
        return Result(title="x")

    plugin.add_method(query)
    assert getattr(query, '_is_registered_method', False) is True


def test_registered_method_can_be_used_as_action():
    plugin = Plugin()

    @plugin.on_method
    def action_handler():
        pass

    r = Result(title="x")
    r.add_action(action_handler)
    assert r.json_rpc_action['Method'] == 'action_handler'
