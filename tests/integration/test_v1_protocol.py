from __future__ import annotations

"""
Integration tests for the V1 (command-line JSON-RPC) protocol.

In V1, Flow Launcher passes the request as a JSON string in sys.argv[1] and
reads the response from stdout. The plugin process is spawned fresh per query.
"""

import asyncio
from typing import Any
from unittest.mock import patch

from pyflowlauncher import Plugin, Result
from pyflowlauncher.launcher import FlowLauncherV1


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def run(plugin: Plugin, request: dict) -> dict | None:
    """Run a V1 plugin with a single request; return whatever was sent to stdout."""
    sent = []

    async def dispatch(method: str, params: list) -> Any:
        return await plugin._event_handler.trigger_event(method, *params)

    with patch.object(plugin._launcher._client, 'recieve', return_value=request), \
         patch.object(plugin._launcher._client, 'send', side_effect=sent.append):
        asyncio.run(plugin._launcher.run(dispatch))

    return sent[0] if sent else None


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestV1Query:

    def test_query_returns_results(self):
        plugin = Plugin(launcher=FlowLauncherV1())

        @plugin.on_method
        def query(q: str):
            yield Result(title=f"V1: {q}")

        response = run(plugin, {'method': 'query', 'parameters': ['hello'], 'settings': {}})
        assert response is not None
        assert response['Result'][0]['Title'] == 'V1: hello'

    def test_query_multiple_results(self):
        plugin = Plugin(launcher=FlowLauncherV1())

        @plugin.on_method
        def query(q: str):
            yield Result(title="first")
            yield Result(title="second")

        response = run(plugin, {'method': 'query', 'parameters': ['x'], 'settings': {}})
        titles = [r['Title'] for r in response['Result']]
        assert titles == ['first', 'second']

    def test_empty_query_string(self):
        plugin = Plugin(launcher=FlowLauncherV1())

        @plugin.on_method
        def query(q: str):
            yield Result(title=f"got: '{q}'")

        response = run(plugin, {'method': 'query', 'parameters': [''], 'settings': {}})
        assert response['Result'][0]['Title'] == "got: ''"

    def test_no_result_sends_nothing(self):
        plugin = Plugin(launcher=FlowLauncherV1())

        @plugin.on_method
        def query(q: str):
            return None

        response = run(plugin, {'method': 'query', 'parameters': [''], 'settings': {}})
        assert response is None


class TestV1Settings:

    def test_settings_available_after_run(self):
        plugin = Plugin(launcher=FlowLauncherV1())

        @plugin.on_method
        def query(q: str):
            return Result(title="ok")

        run(plugin, {'method': 'query', 'parameters': [''], 'settings': {'api_key': 'secret'}})
        assert plugin.settings == {'api_key': 'secret'}

    def test_missing_settings_defaults_to_empty(self):
        plugin = Plugin(launcher=FlowLauncherV1())

        @plugin.on_method
        def query(q: str):
            return Result(title="ok")

        run(plugin, {'method': 'query', 'parameters': ['']})
        assert plugin.settings == {}


class TestV1CustomMethods:

    def test_non_query_method_dispatched(self):
        plugin = Plugin(launcher=FlowLauncherV1())
        called_with = []

        @plugin.on_method
        def on_result_selected(params: list):
            called_with.extend(params)

        run(plugin, {'method': 'on_result_selected', 'parameters': [['arg1', 'arg2']], 'settings': {}})
        assert called_with == ['arg1', 'arg2']
