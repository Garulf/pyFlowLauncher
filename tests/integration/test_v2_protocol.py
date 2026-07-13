"""
Integration tests for the V2 (streaming JSON-RPC) protocol.

Simulates the exact messages Flow Launcher sends over the persistent stdin/stdout
pipe and verifies responses match the JsonRPCQueryResponseModel structure.

Regressions covered:
- 'params' key (JSON-RPC 2.0) vs 'parameters' key — wrong key caused TypeError → bad response
- Response result must be a dict {result:[...]} not a bare array — array fails deserialization
- '$/cancelRequest' notifications must be silently ignored
- Exception responses must be valid objects, not bare arrays
"""

import asyncio
import json
from io import StringIO
from typing import Any
from unittest.mock import patch

from pyflowlauncher import Plugin, Result
from pyflowlauncher.launcher import FlowLauncherV2


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_plugin() -> Plugin:
    plugin = Plugin(launcher=FlowLauncherV2())

    @plugin.on_method
    def query(q: str):
        yield Result(title=f"Hello, {q or 'World'}!", subtitle="sub", icon="icon.png")

    return plugin


def run(plugin: Plugin, messages: list, dispatch=None) -> list:
    """Feed newline-delimited JSON messages to a V2 plugin; return parsed responses."""
    stdin_text = '\n'.join(json.dumps(m) for m in messages) + '\n'
    responses = []

    if dispatch is None:
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


def query_response(responses: list, request_id: int) -> dict:
    return next(r for r in responses if r.get('id') == request_id)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestV2QueryFormat:

    def test_params_key_dispatches_correctly(self):
        """Flow Launcher sends 'params' (JSON-RPC 2.0), not 'parameters'."""
        plugin = make_plugin()
        responses = run(plugin, [
            {'id': 1, 'method': 'query', 'params': [{'search': 'World', 'trimmedQuery': 'World'}, {}]},
            {'id': 2, 'method': 'close', 'params': []},
        ])
        resp = query_response(responses, 1)
        assert resp['id'] == 1
        assert resp['result']['result'][0]['Title'] == 'Hello, World!'

    def test_parameters_key_accepted_as_fallback(self):
        """The legacy 'parameters' key must still work for compatibility."""
        plugin = make_plugin()
        responses = run(plugin, [
            {'id': 1, 'method': 'query', 'parameters': [{'search': 'compat'}, {}]},
            {'id': 2, 'method': 'close', 'parameters': []},
        ])
        assert query_response(responses, 1)['result']['result'][0]['Title'] == 'Hello, compat!'

    def test_response_result_is_object_not_array(self):
        """result field must be an object {result:[...]}, not a bare array.

        Flow Launcher deserialises it as JsonRPCQueryResponseModel (a C# record);
        a bare array causes JsonException at Path:$, BytePosition:1.
        """
        plugin = make_plugin()
        responses = run(plugin, [
            {'id': 1, 'method': 'query', 'params': [{'search': 'hi'}, {}]},
            {'id': 2, 'method': 'close', 'params': []},
        ])
        inner = query_response(responses, 1)['result']
        assert isinstance(inner, dict), "result must be an object, not an array"
        assert isinstance(inner['result'], list)

    def test_response_id_matches_request(self):
        plugin = make_plugin()
        responses = run(plugin, [
            {'id': 42, 'method': 'query', 'params': [{'search': 'x'}, {}]},
            {'id': 43, 'method': 'close', 'params': []},
        ])
        assert query_response(responses, 42)['id'] == 42

    def test_result_items_use_pascal_case_fields(self):
        """Result items must use PascalCase matching Flow Launcher's Result class."""
        plugin = make_plugin()
        responses = run(plugin, [
            {'id': 1, 'method': 'query', 'params': [{'search': 'Test'}, {}]},
            {'id': 2, 'method': 'close', 'params': []},
        ])
        item = query_response(responses, 1)['result']['result'][0]
        assert 'Title' in item
        assert 'SubTitle' in item

    def test_empty_search_string(self):
        plugin = make_plugin()
        responses = run(plugin, [
            {'id': 1, 'method': 'query', 'params': [{'search': '', 'trimmedQuery': ''}, {}]},
            {'id': 2, 'method': 'close', 'params': []},
        ])
        assert query_response(responses, 1)['result']['result'][0]['Title'] == 'Hello, World!'

    def test_action_keyword_not_leaked_into_search(self):
        """Typing only the action keyword sends {'search': '', 'trimmedQuery': 'kw'};
        the handler must receive '' — not fall back to the keyword-bearing trimmedQuery."""
        received = []
        plugin = Plugin(launcher=FlowLauncherV2())

        @plugin.on_method
        def query(q: str):
            received.append(q)
            yield Result(title="ok")

        run(plugin, [
            {'id': 1, 'method': 'query',
             'params': [{'search': '', 'trimmedQuery': 'kw', 'rawQuery': 'kw',
                         'actionKeyword': 'kw'}, {}]},
            {'id': 2, 'method': 'close', 'params': []},
        ])
        assert received == ['']


class TestV2Lifecycle:

    def test_initialize_not_dispatched_to_plugin(self):
        plugin = make_plugin()
        dispatched = []

        async def dispatch(method: str, params: list) -> Any:
            dispatched.append(method)
            return await plugin._event_handler.trigger_event(method, *params)

        run(plugin, [
            {'id': 1, 'method': 'initialize', 'params': []},
            {'id': 2, 'method': 'close', 'params': []},
        ], dispatch=dispatch)
        assert 'initialize' not in dispatched

    def test_initialize_returns_empty_result(self):
        plugin = make_plugin()
        responses = run(plugin, [
            {'id': 1, 'method': 'initialize', 'params': []},
            {'id': 2, 'method': 'close', 'params': []},
        ])
        init_resp = next(r for r in responses if r.get('id') == 1)
        assert init_resp['result'] == {}

    def test_reload_data_not_dispatched(self):
        plugin = make_plugin()
        dispatched = []

        async def dispatch(method: str, params: list) -> Any:
            dispatched.append(method)
            return await plugin._event_handler.trigger_event(method, *params)

        run(plugin, [
            {'id': 1, 'method': 'reload_data', 'params': []},
            {'id': 2, 'method': 'close', 'params': []},
        ], dispatch=dispatch)
        assert 'reload_data' not in dispatched

    def test_close_stops_loop(self):
        plugin = make_plugin()
        dispatched = []

        async def dispatch(method: str, params: list) -> Any:
            dispatched.append(method)
            return await plugin._event_handler.trigger_event(method, *params)

        run(plugin, [
            {'id': 1, 'method': 'close', 'params': []},
            {'id': 2, 'method': 'query', 'params': [{'search': 'after'}, {}]},
        ], dispatch=dispatch)
        assert 'query' not in dispatched


class TestV2Notifications:

    def test_cancel_request_silently_ignored(self):
        """$/cancelRequest is a notification; must not be dispatched or cause errors."""
        plugin = make_plugin()
        dispatched = []

        async def dispatch(method: str, params: list) -> Any:
            dispatched.append(method)
            return await plugin._event_handler.trigger_event(method, *params)

        run(plugin, [
            {'id': 1, 'method': 'query', 'params': [{'search': 'hi'}, {}]},
            {'method': '$/cancelRequest', 'params': {'id': 1}},
            {'id': 2, 'method': 'close', 'params': []},
        ], dispatch=dispatch)
        assert '$/cancelRequest' not in dispatched

    def test_dollar_prefix_methods_ignored(self):
        """Any method starting with '$/' must be silently skipped."""
        plugin = Plugin(launcher=FlowLauncherV2())
        dispatched = []

        async def dispatch(method: str, params: list) -> Any:
            dispatched.append(method)
            return None

        run(plugin, [
            {'method': '$/progress', 'params': {}},
            {'id': 1, 'method': 'close', 'params': []},
        ], dispatch=dispatch)
        assert not any(m.startswith('$/') for m in dispatched)


class TestV2ErrorHandling:

    def test_unknown_method_returns_valid_object_response(self):
        """Error response must be a dict, not a bare array.

        Regression: exception handler sent result:[] which failed JsonRPCQueryResponseModel
        deserialization in Flow Launcher (Path:$, BytePosition:1).
        """
        plugin = Plugin(launcher=FlowLauncherV2())
        responses = run(plugin, [
            {'id': 1, 'method': 'nonexistent', 'params': []},
            {'id': 2, 'method': 'close', 'params': []},
        ])
        resp = query_response(responses, 1)
        assert isinstance(resp.get('result'), dict), \
            "error response result must be a dict, not an array"

    def test_exception_in_handler_loop_continues(self):
        """An exception in one dispatch must not kill the event loop."""
        plugin = Plugin(launcher=FlowLauncherV2())
        call_count = [0]

        @plugin.on_method
        def query(q: str):
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("boom")
            yield Result(title="recovered")

        responses = run(plugin, [
            {'id': 1, 'method': 'query', 'params': [{'search': 'a'}, {}]},
            {'id': 2, 'method': 'query', 'params': [{'search': 'b'}, {}]},
            {'id': 3, 'method': 'close', 'params': []},
        ])
        assert call_count[0] == 2
        second = query_response(responses, 2)
        assert second['result']['result'][0]['Title'] == 'recovered'

    def test_invalid_json_line_skipped(self):
        # run() can't inject a raw invalid-JSON line, so build stdin manually.
        plugin = make_plugin()
        stdin_text = (
            'not-valid-json\n'
            + json.dumps({'id': 1, 'method': 'query', 'params': [{'search': 'ok'}, {}]}) + '\n'
            + json.dumps({'id': 2, 'method': 'close', 'params': []}) + '\n'
        )
        responses = []

        async def dispatch(method: str, params: list) -> Any:
            return await plugin._event_handler.trigger_event(method, *params)

        async def _inner():
            with patch('sys.stdin', StringIO(stdin_text)), \
                 patch('sys.stdout', StringIO()) as out:
                await plugin._launcher.run(dispatch)
                out.seek(0)
                for line in out.read().splitlines():
                    if line.strip():
                        responses.append(json.loads(line))

        asyncio.run(_inner())
        assert query_response(responses, 1)['result']['result'][0]['Title'] == 'Hello, ok!'


class TestV2Actions:
    """Action execution (JsonRPCAction) over the V2 protocol.

    Flow Launcher V2 executes actions via StreamJsonRpc's
    RPC.InvokeAsync(method, argument: Parameters) — the single-argument
    overload, which wraps the whole Parameters list in a one-element array:
    the wire is params=[[p1, p2]], unlike V1's parameters=[p1, p2].
    """

    def _plugin_with_action(self, calls: list) -> Plugin:
        plugin = Plugin(launcher=FlowLauncherV2())

        @plugin.on_method
        def my_action(a, b):
            calls.append((a, b))

        @plugin.on_method
        def no_arg_action():
            calls.append(())

        return plugin

    def test_action_parameters_unwrapped(self):
        calls = []
        plugin = self._plugin_with_action(calls)
        run(plugin, [
            {'id': 1, 'method': 'my_action', 'params': [['a', 'b']]},
            {'id': 2, 'method': 'close', 'params': []},
        ])
        assert calls == [('a', 'b')]

    def test_action_with_empty_parameters(self):
        calls = []
        plugin = self._plugin_with_action(calls)
        run(plugin, [
            {'id': 1, 'method': 'no_arg_action', 'params': [[]]},
            {'id': 2, 'method': 'close', 'params': []},
        ])
        assert calls == [()]

    def test_action_response_is_execute_response(self):
        """Flow deserializes the result as JsonRPCExecuteResponse(bool Hide = true),
        so both {} and {'hide': True} mean 'hide the window'."""
        calls = []
        plugin = self._plugin_with_action(calls)
        responses = run(plugin, [
            {'id': 1, 'method': 'my_action', 'params': [['a', 'b']]},
            {'id': 2, 'method': 'close', 'params': []},
        ])
        assert query_response(responses, 1)['result'] in ({}, {'hide': True})

    def test_context_menu_receives_context_data_as_single_argument(self):
        """context_menu keeps V1 parity: one argument, the ContextData list.

        Flow V2 sends params=[ContextData] (InvokeWithCancellationAsync with a
        one-element argument array) — it must NOT be unwrapped like actions.
        """
        received = []
        plugin = Plugin(launcher=FlowLauncherV2())

        @plugin.on_method
        def context_menu(data):
            received.append(data)
            return Result(title="ctx item")

        run(plugin, [
            {'id': 1, 'method': 'context_menu', 'params': [['ctx1', 'ctx2']]},
            {'id': 2, 'method': 'close', 'params': []},
        ])
        assert received == [['ctx1', 'ctx2']]


class TestV2Settings:

    def test_settings_stored_from_query_params(self):
        """V2 sends settings as the second query param:
        RPC.InvokeWithCancellationAsync("query", new object[] { query, Settings.Inner })."""
        plugin = Plugin(launcher=FlowLauncherV2())

        @plugin.on_method
        def query(q: str):
            yield Result(title="ok")

        run(plugin, [
            {'id': 1, 'method': 'query',
             'params': [{'search': 'x', 'trimmedQuery': 'x'}, {'api_key': 'secret'}]},
            {'id': 2, 'method': 'close', 'params': []},
        ])
        assert plugin._launcher.settings == {'api_key': 'secret'}

    def test_query_settings_param_not_passed_to_handler(self):
        """The settings dict must be consumed, not passed as a query argument."""
        received = []
        plugin = Plugin(launcher=FlowLauncherV2())

        @plugin.on_method
        def query(*args):
            received.append(args)
            yield Result(title="ok")

        run(plugin, [
            {'id': 1, 'method': 'query',
             'params': [{'search': 'x'}, {'api_key': 'secret'}]},
            {'id': 2, 'method': 'close', 'params': []},
        ])
        assert received == [('x',)]

    def test_settings_stored_from_request(self):
        plugin = Plugin(launcher=FlowLauncherV2())

        @plugin.on_method
        def query(q: str):
            yield Result(title="ok")

        run(plugin, [
            {'id': 1, 'method': 'initialize', 'params': [], 'settings': {'key': 'val'}},
            {'id': 2, 'method': 'close', 'params': []},
        ])
        assert plugin._launcher.settings == {'key': 'val'}


class TestV2FuzzySearch:

    def test_fuzzy_search_round_trip(self):
        """Handler calls api.fuzzy_search; host responds; result reaches handler."""
        plugin = Plugin(launcher=FlowLauncherV2())
        match_results = []

        @plugin.on_method
        async def query(q: str):
            match = await plugin.launcher.api.fuzzy_search(q, 'Hello World')
            match_results.append(match)
            yield Result(title=f"score:{match.score}")

        # The query request comes in first; then the FuzzySearch response from
        # the host; then close to terminate the loop.
        fuzzy_response = json.dumps({
            'id': 1,
            'result': {'success': True, 'score': 95, 'rawScore': 95,
                       'matchData': [0, 1, 2], 'searchPrecision': 50},
        })
        stdin_text = (
            json.dumps({'id': 10, 'method': 'query',
                        'params': [{'search': 'hel', 'trimmedQuery': 'hel'}]}) + '\n'
            + fuzzy_response + '\n'
            + json.dumps({'id': 11, 'method': 'close', 'params': []}) + '\n'
        )
        responses = []

        async def dispatch(method: str, params: list) -> Any:
            return await plugin._event_handler.trigger_event(method, *params)

        async def _inner():
            with patch('sys.stdin', StringIO(stdin_text)), \
                 patch('sys.stdout', StringIO()) as out:
                await plugin._launcher.run(dispatch)
                out.seek(0)
                for line in out.read().splitlines():
                    if line.strip():
                        responses.append(json.loads(line))

        asyncio.run(_inner())

        assert len(match_results) == 1
        assert match_results[0].matched is True
        assert match_results[0].score == 95
        query_resp = query_response(responses, 10)
        assert query_resp['result']['result'][0]['Title'] == 'score:95'


