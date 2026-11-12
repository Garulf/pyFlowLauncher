"""V2 replies take their shape from the request kind.

The host reads replies to ``query`` and ``context_menu`` as
JsonRPCQueryResponseModel and replies to everything else as
JsonRPCExecuteResponse, so the shape must not depend on what a handler
returned.
"""

import asyncio
import json
import logging
from io import StringIO
from typing import Any
from unittest.mock import patch

import pytest

from pyflowlauncher import Plugin, Result, api
from pyflowlauncher.launcher import FlowLauncherV2


@pytest.fixture
def caplog(caplog, monkeypatch):
    monkeypatch.setattr(logging.getLogger('pyflowlauncher'), 'propagate', True)
    return caplog


QUERY_KEYS = {'result', 'settingsChange', 'debugMessage'}


def run(plugin: Plugin, messages: list) -> list:
    stdin_text = '\n'.join(json.dumps(m) for m in messages) + '\n'
    responses = []

    async def dispatch(method: str, params: list) -> Any:
        return await plugin._event_handler.trigger_event(method, *params)

    async def _run():
        with patch('sys.stdin', StringIO(stdin_text)), \
             patch('sys.stdout', StringIO()) as out:
            await plugin._launcher.run(dispatch)
            out.seek(0)
            for line in out.read().splitlines():
                if line.strip():
                    responses.append(json.loads(line))

    asyncio.run(_run())
    return responses


def reply(responses: list, request_id: int) -> dict:
    return next(r for r in responses if r.get('id') == request_id and 'method' not in r)


def run_query(plugin: Plugin) -> dict:
    responses = run(plugin, [
        {'id': 1, 'method': 'query', 'params': [{'search': 'x'}, {}]},
        {'id': 2, 'method': 'close', 'params': []},
    ])
    return reply(responses, 1)


def titles(body: dict) -> list:
    return [r['Title'] for r in body['result']]


class TestQueryReplies:

    def test_sync_generator_exception_handler_answers_failed_query(self):
        plugin = Plugin(launcher=FlowLauncherV2())

        @plugin.on_method
        def query(q):
            raise ValueError('boom')

        @plugin.on_except(ValueError)
        def handler(exc):
            yield Result(title=f'error: {exc}')

        body = run_query(plugin)['result']
        assert set(body) == QUERY_KEYS
        assert titles(body) == ['error: boom']

    def test_async_handler_returning_sync_generator(self):
        plugin = Plugin(launcher=FlowLauncherV2())

        def results():
            yield Result(title='a')
            yield Result(title='b')

        async def query(q):
            return results()
        plugin.add_method(query)

        body = run_query(plugin)['result']
        assert titles(body) == ['a', 'b']

    def test_query_returning_none_is_query_shaped(self):
        plugin = Plugin(launcher=FlowLauncherV2())

        @plugin.on_method
        def query(q):
            return None

        body = run_query(plugin)['result']
        assert set(body) == QUERY_KEYS
        assert body['result'] == []

    def test_context_menu_returning_none_is_query_shaped(self):
        plugin = Plugin(launcher=FlowLauncherV2())

        @plugin.on_method
        def context_menu(data):
            return None

        responses = run(plugin, [
            {'id': 1, 'method': 'context_menu', 'params': [['x']]},
            {'id': 2, 'method': 'close', 'params': []},
        ])
        body = reply(responses, 1)['result']
        assert set(body) == QUERY_KEYS
        assert body['result'] == []

    def test_query_yielding_command_and_results_forwards_and_keeps_results(self):
        plugin = Plugin(launcher=FlowLauncherV2())

        @plugin.on_method
        def query(q):
            yield Result(title='a')
            yield api.change_query('new')
            yield Result(title='b')

        responses = run(plugin, [
            {'id': 5, 'method': 'query', 'params': [{'search': 'x'}, {}]},
            {'id': 1, 'result': None},
            {'id': 6, 'method': 'close', 'params': []},
        ])
        forwarded = next(r for r in responses if r.get('method') == 'ChangeQuery')
        assert forwarded['params'] == ['new', False]
        body = reply(responses, 5)['result']
        assert set(body) == QUERY_KEYS
        assert titles(body) == ['a', 'b']

    def test_failed_query_keeps_internal_error_body(self):
        plugin = Plugin(launcher=FlowLauncherV2())

        @plugin.on_method
        def query(q):
            raise ValueError('boom')

        body = run_query(plugin)['result']
        assert body == {'result': [], 'debugMessage': 'Internal error', 'settingsChange': None}


class TestActionReplies:

    def _action(self, plugin: Plugin) -> dict:
        responses = run(plugin, [
            {'id': 3, 'method': 'act', 'params': [[]]},
            {'id': 4, 'method': 'close', 'params': []},
        ])
        return reply(responses, 3)

    def test_failed_action_without_handler_gets_execute_reply(self):
        plugin = Plugin(launcher=FlowLauncherV2())

        def act():
            raise ValueError('boom')
        plugin.add_method(act)

        resp = self._action(plugin)
        assert resp['result'] == {'hide': False}
        assert resp.get('error') is None

    def test_action_returning_results_gets_execute_reply(self):
        plugin = Plugin(launcher=FlowLauncherV2())

        def act():
            return [Result(title='ignored')]
        plugin.add_method(act)

        assert self._action(plugin)['result'] == {'hide': True}

    def test_action_returning_none_gets_execute_reply(self):
        plugin = Plugin(launcher=FlowLauncherV2())

        def act():
            return None
        plugin.add_method(act)

        assert self._action(plugin)['result'] == {'hide': True}


class TestDroppedItemsLogged:

    def test_async_generator_logs_dropped_items(self, caplog):
        plugin = Plugin(launcher=FlowLauncherV2())

        async def query(q):
            yield Result(title='a')
            yield 'not a result'
        plugin.add_method(query)

        with caplog.at_level(logging.WARNING):
            body = run_query(plugin)['result']
        assert titles(body) == ['a']
        assert "'not a result'" in caplog.text

    def test_async_list_logs_dropped_items(self, caplog):
        plugin = Plugin(launcher=FlowLauncherV2())

        async def query(q):
            return [Result(title='a'), 42]
        plugin.add_method(query)

        with caplog.at_level(logging.WARNING):
            body = run_query(plugin)['result']
        assert titles(body) == ['a']
        assert '42' in caplog.text
