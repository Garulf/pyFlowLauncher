"""DontHideAfterAction works on V2 the way it does on V1.

The V2 host takes the hide decision from the plugin's reply to the action
request and never reads DontHideAfterAction, which it does not send back.
The launcher remembers the flag from the results it sent.
"""

import asyncio
import json
from io import StringIO
from typing import Any
from unittest.mock import patch

from pyflowlauncher import Plugin, Result, api
from pyflowlauncher.launcher import FlowLauncherV2


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


def query_request(request_id: int) -> dict:
    return {'id': request_id, 'method': 'query', 'params': [{'search': 'x'}, {}]}


def action(request_id: int, method: str, parameters: list) -> dict:
    return {'id': request_id, 'method': method, 'params': [parameters]}


def close(request_id: int) -> dict:
    return {'id': request_id, 'method': 'close', 'params': []}


def sent_action(responses: list, query_id: int, index: int = 0) -> dict:
    return reply(responses, query_id)['result']['result'][index]['JsonRPCAction']


def plugin_with_action(dont_hide: bool) -> Plugin:
    plugin = Plugin(launcher=FlowLauncherV2())

    @plugin.on_method
    def keep(item, count):
        return None

    @plugin.on_method
    def query(q):
        yield Result(title='r').add_action(keep, ['a', 1], dont_hide_after_action=dont_hide)

    return plugin


class TestPluginMethodAction:

    def test_flag_set_keeps_window_open(self):
        responses = run(plugin_with_action(True), [
            query_request(1), action(2, 'keep', ['a', 1]), close(3),
        ])
        assert reply(responses, 2)['result'] == {'hide': False}

    def test_flag_not_set_hides(self):
        responses = run(plugin_with_action(False), [
            query_request(1), action(2, 'keep', ['a', 1]), close(3),
        ])
        assert reply(responses, 2)['result'] == {'hide': True}

    def test_key_built_from_sent_json_matches_received_json(self):
        responses = run(plugin_with_action(True), [query_request(1), close(2)])
        sent = sent_action(responses, 1)
        responses = run(plugin_with_action(True), [
            query_request(1), action(2, sent['Method'], sent['Parameters']), close(3),
        ])
        assert reply(responses, 2)['result'] == {'hide': False}

    def test_different_parameters_are_a_different_action(self):
        responses = run(plugin_with_action(True), [
            query_request(1), action(2, 'keep', ['b', 1]), close(3),
        ])
        assert reply(responses, 2)['result'] == {'hide': True}

    def test_action_never_sent_in_a_result_hides(self):
        plugin = Plugin(launcher=FlowLauncherV2())

        @plugin.on_method
        def keep(item):
            return None

        responses = run(plugin, [action(1, 'keep', ['a']), close(2)])
        assert reply(responses, 1)['result'] == {'hide': True}

    def test_failed_action_hides_nothing_even_with_flag(self):
        plugin = Plugin(launcher=FlowLauncherV2())

        @plugin.on_method
        def boom(item):
            raise ValueError('boom')

        @plugin.on_method
        def query(q):
            yield Result(title='r').add_action(boom, ['a'], dont_hide_after_action=True)

        responses = run(plugin, [query_request(1), action(2, 'boom', ['a']), close(3)])
        assert reply(responses, 2)['result'] == {'hide': False}


class TestBuiltInCommand:
    # The query runs in its own session: queued ahead of the action, the host
    # reply line is read before the forwarded request is registered.

    def test_command_with_flag_keeps_window_open(self):
        plugin = Plugin(launcher=FlowLauncherV2())

        @plugin.on_method
        def query(q):
            yield Result(title='r').add_action(
                api.copy_to_clipboard('text'), dont_hide_after_action=True)

        responses = run(plugin, [query_request(1), close(9)])
        sent = sent_action(responses, 1)

        responses = run(plugin, [
            action(2, sent['Method'], sent['Parameters']),
            {'id': 1, 'result': None},
            close(3),
        ])
        forwarded = [r for r in responses if r.get('method') == 'CopyToClipboard']
        assert forwarded and forwarded[0]['params'] == ['text', False, True]
        assert reply(responses, 2)['result'] == {'hide': False}

    def test_command_without_flag_hides(self):
        plugin = Plugin(launcher=FlowLauncherV2())

        @plugin.on_method
        def query(q):
            yield Result(title='r').add_action(api.copy_to_clipboard('text'))

        run(plugin, [query_request(1), close(9)])
        responses = run(plugin, [
            action(2, 'Flow.Launcher.CopyToClipboard', ['text', False, True]),
            {'id': 1, 'result': None},
            close(3),
        ])
        assert reply(responses, 2)['result'] == {'hide': True}


class TestRawDictAction:

    def test_raw_dict_with_other_key_casing(self):
        plugin = Plugin(launcher=FlowLauncherV2())

        @plugin.on_method
        def keep(item):
            return None

        @plugin.on_method
        def query(q):
            yield Result(title='r', json_rpc_action={  # type: ignore[typeddict-unknown-key]
                'method': 'keep', 'parameters': ['a'], 'dontHideAfterAction': True,
            })

        responses = run(plugin, [query_request(1), action(2, 'keep', ['a']), close(3)])
        assert reply(responses, 2)['result'] == {'hide': False}

    def test_raw_result_dicts_returned_from_query(self):
        plugin = Plugin(launcher=FlowLauncherV2())

        @plugin.on_method
        def keep(item):
            return None

        @plugin.on_method
        def query(q):
            return {'Result': [{
                'Title': 'r',
                'JsonRPCAction': {'Method': 'keep', 'Parameters': ['a'], 'DontHideAfterAction': True},
            }], 'SettingsChange': None}

        responses = run(plugin, [query_request(1), action(2, 'keep', ['a']), close(3)])
        assert reply(responses, 2)['result'] == {'hide': False}


class TestContextMenu:

    def test_context_menu_item_with_flag(self):
        plugin = Plugin(launcher=FlowLauncherV2())

        @plugin.on_method
        def keep(item):
            return None

        @plugin.on_method
        def context_menu(data):
            yield Result(title='c').add_action(keep, ['ctx'], dont_hide_after_action=True)

        responses = run(plugin, [
            {'id': 1, 'method': 'context_menu', 'params': [['d']]},
            action(2, 'keep', ['ctx']),
            close(3),
        ])
        assert reply(responses, 2)['result'] == {'hide': False}


class TestMostRecentlySentWins:

    def test_flag_flipped_in_a_later_reply(self):
        plugin = Plugin(launcher=FlowLauncherV2())
        flags = iter([True, False])

        @plugin.on_method
        def keep(item):
            return None

        @plugin.on_method
        def query(q):
            yield Result(title='r').add_action(keep, ['a'], dont_hide_after_action=next(flags))

        responses = run(plugin, [
            query_request(1), action(2, 'keep', ['a']),
            query_request(3), action(4, 'keep', ['a']),
            close(5),
        ])
        assert reply(responses, 2)['result'] == {'hide': False}
        assert reply(responses, 4)['result'] == {'hide': True}

    def test_flag_flipped_back_on(self):
        plugin = Plugin(launcher=FlowLauncherV2())
        flags = iter([False, True])

        @plugin.on_method
        def keep(item):
            return None

        @plugin.on_method
        def query(q):
            yield Result(title='r').add_action(keep, ['a'], dont_hide_after_action=next(flags))

        responses = run(plugin, [
            query_request(1), query_request(2), action(3, 'keep', ['a']), close(4),
        ])
        assert reply(responses, 3)['result'] == {'hide': False}


class TestMemoryIsBounded:

    def test_oldest_flags_are_forgotten(self):
        launcher = FlowLauncherV2()
        limit = launcher._DONT_HIDE_MEMORY
        actions = [
            {'Title': str(i), 'JsonRPCAction': {
                'Method': 'keep', 'Parameters': [i], 'DontHideAfterAction': True}}
            for i in range(limit + 1)
        ]
        launcher._query_reply('query', {'Result': actions, 'SettingsChange': None})
        assert launcher._action_reply('keep', [0]) == {'hide': True}
        assert launcher._action_reply('keep', [limit]) == {'hide': False}
