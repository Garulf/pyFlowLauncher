import asyncio
import functools
import json
from io import StringIO
from typing import Any
from unittest.mock import patch

import pytest

from pyflowlauncher import Plugin, Result
from pyflowlauncher.launcher import FlowLauncherV1, FlowLauncherV2
from pyflowlauncher.result import MethodNotRegisteredError


def action_name(method, *args) -> str:
    return Result(title="x").add_action(method, list(args)).json_rpc_action["Method"]


def test_mixed_case_function_name_matches_registered_name():
    plugin = Plugin(launcher=FlowLauncherV1())

    def openItem(path):
        return None

    registered = plugin.add_method(openItem)
    assert registered == "openitem"
    assert action_name(openItem) == registered


def test_explicit_name_is_sent_by_add_action():
    plugin = Plugin(launcher=FlowLauncherV1())

    def handler():
        return None

    registered = plugin.add_method(handler, name="Open_Thing")
    assert registered == "Open_Thing"
    assert action_name(handler) == "Open_Thing"


def test_query_and_context_menu_keep_lowercase_names():
    plugin = Plugin(launcher=FlowLauncherV1())

    def query(q):
        return None

    def context_menu(data):
        return None

    assert plugin.add_method(query) == "query"
    assert plugin.add_method(context_menu) == "context_menu"


def test_class_instance_registers_under_lowercased_class_name():
    plugin = Plugin(launcher=FlowLauncherV1())

    class OpenFolder:
        def __call__(self, path):
            return None

    instance = OpenFolder()
    assert plugin.add_method(instance) == "openfolder"
    assert action_name(instance) == "openfolder"


def test_partial_registers_under_wrapped_function_name():
    plugin = Plugin(launcher=FlowLauncherV1())

    def openWith(app, path):
        return None

    bound = functools.partial(openWith, "code")
    assert plugin.add_method(bound) == "openwith"
    assert action_name(bound) == "openwith"


def test_bound_method_can_be_registered_and_used_as_action():
    plugin = Plugin(launcher=FlowLauncherV1())

    class Handlers:
        def openItem(self, path):
            return None

    handlers = Handlers()
    assert plugin.add_method(handlers.openItem) == "openitem"
    assert action_name(handlers.openItem, "p") == "openitem"


def test_bound_method_of_another_instance_is_not_registered():
    plugin = Plugin(launcher=FlowLauncherV1())

    class Handlers:
        def open(self):
            return None

    plugin.add_method(Handlers().open)
    with pytest.raises(MethodNotRegisteredError):
        Result(title="x").add_action(Handlers().open)


def test_unregistered_function_raises():
    def never_registered():
        return None

    with pytest.raises(MethodNotRegisteredError, match="never_registered"):
        Result(title="x").add_action(never_registered)


def test_unregistered_callable_without_name_raises_cleanly():
    class Nameless:
        def __call__(self):
            return None

    with pytest.raises(MethodNotRegisteredError):
        Result(title="x").add_action(Nameless())


def _make_plugin(launcher):
    plugin = Plugin(launcher=launcher)
    calls = []

    def openItem(path):
        calls.append(path)

    @plugin.on_method
    def query(q):
        plugin.add_method(openItem)
        return Result(title="hit").add_action(openItem, ["the/path"])

    return plugin, calls


def _dispatcher(plugin):
    async def dispatch(method: str, params: list) -> Any:
        return await plugin._event_handler.trigger_event(method, *params)
    return dispatch


def _run_v1(plugin, request: dict) -> Any:
    sent = []
    client = plugin._launcher._client
    with patch.object(client, 'receive', return_value=request), \
            patch.object(client, 'send', side_effect=sent.append):
        asyncio.run(plugin._launcher.run(_dispatcher(plugin)))
    return sent[0] if sent else None


def _run_v2(plugin, messages: list) -> list:
    stdin_text = '\n'.join(json.dumps(m) for m in messages) + '\n'

    async def _run():
        with patch('sys.stdin', StringIO(stdin_text)), patch('sys.stdout', StringIO()) as out:
            await plugin._launcher.run(_dispatcher(plugin))
            return [json.loads(line) for line in out.getvalue().splitlines() if line.strip()]

    return asyncio.run(_run())


def test_v1_host_can_call_the_action_it_was_given():
    plugin, calls = _make_plugin(FlowLauncherV1())
    response = _run_v1(plugin, {'method': 'query', 'parameters': ['x']})
    action = response['Result'][0]['JsonRPCAction']
    _run_v1(plugin, {'method': action['Method'], 'parameters': action['Parameters']})
    assert calls == ["the/path"]


def test_v2_host_can_call_the_action_it_was_given():
    plugin, calls = _make_plugin(FlowLauncherV2())
    responses = _run_v2(plugin, [
        {'id': 1, 'method': 'query', 'params': [{'search': 'x'}, {}]},
    ])
    action = next(r for r in responses if r.get('id') == 1)['result']['result'][0]['JsonRPCAction']
    responses = _run_v2(plugin, [
        {'id': 2, 'method': action['Method'], 'params': action['Parameters']},
        {'id': 3, 'method': 'close', 'params': []},
    ])
    assert calls == ["the/path"]
    assert next(r for r in responses if r.get('id') == 2).get('error') is None
