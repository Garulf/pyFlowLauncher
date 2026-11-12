import asyncio
import logging

import pytest

from pyflowlauncher import Command, Result, api, handle_response
from pyflowlauncher.event import EventHandler
from pyflowlauncher.result import send_results


@pytest.fixture
def caplog(caplog, monkeypatch):
    monkeypatch.setattr(logging.getLogger('pyflowlauncher'), 'propagate', True)
    return caplog


def normalize(value):
    return asyncio.run(EventHandler()._await_maybe(value))


def test_sync_generator_from_exception_handler_is_collected():
    handler = EventHandler()

    def fails():
        raise ValueError('boom')

    def on_error(exc):
        yield Result(title='oops')

    handler.add_event(fails)
    handler.add_exception_handler(ValueError, on_error)
    out = asyncio.run(handler.trigger_event('fails'))
    assert out == send_results([Result(title='oops')])


def test_coroutine_returning_sync_generator_is_collected():
    def gen():
        yield Result(title='a')

    async def coro():
        return gen()

    assert normalize(coro()) == send_results([Result(title='a')])


def test_coroutine_returning_result_is_wrapped():
    async def coro():
        return Result(title='a')

    assert normalize(coro()) == send_results([Result(title='a')])


def test_built_response_passes_through():
    resp = send_results([Result(title='a')])
    assert normalize(resp) is resp


def test_none_stays_none():
    assert normalize(None) is None


def test_async_list_drops_and_logs_non_results(caplog):
    async def coro():
        return [Result(title='a'), 'junk']

    with caplog.at_level(logging.WARNING):
        out = normalize(coro())
    assert out == send_results([Result(title='a')])
    assert "'junk'" in caplog.text


def test_generator_with_command_and_results_keeps_both():
    def gen():
        yield Result(title='a')
        yield api.hide_app()

    out = handle_response(gen())
    assert isinstance(out, Command)
    assert out == api.hide_app()
    assert out.results == [Result(title='a')]


def test_async_generator_with_command_and_results_keeps_both():
    async def gen():
        yield api.hide_app()
        yield [Result(title='a'), Result(title='b')]

    out = normalize(gen())
    assert isinstance(out, Command)
    assert out.results == [Result(title='a'), Result(title='b')]
