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
from pyflowlauncher.result import send_results


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_plugin() -> Plugin:
    plugin = Plugin(launcher=FlowLauncherV2())

    @plugin.on_method
    def query(q: str):
        yield Result(title=f"Hello, {q or 'World'}!", subtitle="sub", icon="icon.png")

    return plugin


def run(plugin: Plugin, messages: list) -> list:
    """Feed newline-delimited JSON messages to a V2 plugin; return parsed responses."""
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


class TestV2Lifecycle:

    def test_initialize_not_dispatched_to_plugin(self):
        plugin = make_plugin()
        dispatched = []

        async def dispatch(method: str, params: list) -> Any:
            dispatched.append(method)
            return await plugin._event_handler.trigger_event(method, *params)

        stdin_text = (
            json.dumps({'id': 1, 'method': 'initialize', 'params': []}) + '\n'
            + json.dumps({'id': 2, 'method': 'close', 'params': []}) + '\n'
        )
        asyncio.run(_run_with_dispatch(plugin, stdin_text, dispatch))
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

        stdin_text = (
            json.dumps({'id': 1, 'method': 'reload_data', 'params': []}) + '\n'
            + json.dumps({'id': 2, 'method': 'close', 'params': []}) + '\n'
        )
        asyncio.run(_run_with_dispatch(plugin, stdin_text, dispatch))
        assert 'reload_data' not in dispatched

    def test_close_stops_loop(self):
        plugin = make_plugin()
        dispatched = []

        async def dispatch(method: str, params: list) -> Any:
            dispatched.append(method)
            return await plugin._event_handler.trigger_event(method, *params)

        stdin_text = (
            json.dumps({'id': 1, 'method': 'close', 'params': []}) + '\n'
            + json.dumps({'id': 2, 'method': 'query', 'params': [{'search': 'after'}, {}]}) + '\n'
        )
        asyncio.run(_run_with_dispatch(plugin, stdin_text, dispatch))
        assert 'query' not in dispatched


class TestV2Notifications:

    def test_cancel_request_silently_ignored(self):
        """$/cancelRequest is a notification; must not be dispatched or cause errors."""
        plugin = make_plugin()
        dispatched = []

        async def dispatch(method: str, params: list) -> Any:
            dispatched.append(method)
            return await plugin._event_handler.trigger_event(method, *params)

        stdin_text = (
            json.dumps({'id': 1, 'method': 'query', 'params': [{'search': 'hi'}, {}]}) + '\n'
            + json.dumps({'method': '$/cancelRequest', 'params': {'id': 1}}) + '\n'
            + json.dumps({'id': 2, 'method': 'close', 'params': []}) + '\n'
        )
        asyncio.run(_run_with_dispatch(plugin, stdin_text, dispatch))
        assert '$/cancelRequest' not in dispatched

    def test_dollar_prefix_methods_ignored(self):
        """Any method starting with '$/' must be silently skipped."""
        plugin = Plugin(launcher=FlowLauncherV2())
        dispatched = []

        async def dispatch(method: str, params: list) -> Any:
            dispatched.append(method)
            return None

        stdin_text = (
            json.dumps({'method': '$/progress', 'params': {}}) + '\n'
            + json.dumps({'id': 1, 'method': 'close', 'params': []}) + '\n'
        )
        asyncio.run(_run_with_dispatch(plugin, stdin_text, dispatch))
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
        plugin = make_plugin()
        responses = run(plugin, [])

        stdin_text = (
            'not-valid-json\n'
            + json.dumps({'id': 1, 'method': 'query', 'params': [{'search': 'ok'}, {}]}) + '\n'
            + json.dumps({'id': 2, 'method': 'close', 'params': []}) + '\n'
        )
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
        assert query_response(responses, 1)['result']['result'][0]['Title'] == 'Hello, ok!'


class TestV2Settings:

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


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

async def _run_with_dispatch(plugin: Plugin, stdin_text: str, dispatch) -> list:
    responses = []
    with patch('sys.stdin', StringIO(stdin_text)), \
         patch('sys.stdout', StringIO()) as out:
        await plugin._launcher.run(dispatch)
        out.seek(0)
        for line in out.read().splitlines():
            if line.strip():
                responses.append(json.loads(line))
    return responses
