import asyncio
import json
from io import StringIO
from unittest.mock import patch

import pytest

from pyflowlauncher import Plugin, Result
from pyflowlauncher.command import Command
from pyflowlauncher.launcher import FlowLauncherV1, FlowLauncherV2


def do_stuff(params):
    return None


def test_action_returns_command_with_registered_name():
    plugin = Plugin()
    action = plugin.action(do_stuff, ["stuff"])
    assert isinstance(action, Command)
    assert action == {"Method": "do_stuff", "Parameters": ["stuff"]}


def test_action_defaults_to_empty_parameters():
    plugin = Plugin()
    assert plugin.action(do_stuff) == {"Method": "do_stuff", "Parameters": []}


def test_action_works_with_json_rpc_action_argument():
    plugin = Plugin()
    result = Result(title="t", json_rpc_action=plugin.action(do_stuff, ["stuff"]))
    assert result.to_json()["JsonRPCAction"] == {"Method": "do_stuff", "Parameters": ["stuff"]}


def test_action_works_with_add_action():
    plugin = Plugin()
    result = Result(title="t").add_action(plugin.action(do_stuff, ["stuff"]))
    assert result.to_json()["JsonRPCAction"] == {
        "Method": "do_stuff",
        "Parameters": ["stuff"],
        "DontHideAfterAction": False,
    }


def _plugin_with_action(launcher, attach):
    plugin = Plugin(launcher=launcher)

    @plugin.on_method
    def query(q: str):
        yield attach(plugin, Result(title="t"))

    return plugin


ATTACHERS = {
    "json_rpc_action": lambda plugin, r: Result(title="t", json_rpc_action=plugin.action(do_stuff, ["stuff"])),
    "add_action": lambda plugin, r: r.add_action(plugin.action(do_stuff, ["stuff"])),
}


@pytest.mark.parametrize("attach", ATTACHERS.values(), ids=ATTACHERS.keys())
def test_v1_query_carries_action(attach):
    plugin = _plugin_with_action(FlowLauncherV1(), attach)
    sent = []

    async def dispatch(method, params):
        return await plugin._event_handler.trigger_event(method, *params)

    request = {"method": "query", "parameters": ["x"], "settings": {}}
    with patch.object(plugin._launcher._client, "receive", return_value=request), \
            patch.object(plugin._launcher._client, "send", side_effect=sent.append):
        asyncio.run(plugin._launcher.run(dispatch))

    action = sent[0]["Result"][0]["JsonRPCAction"]
    assert action["Method"] == "do_stuff"
    assert action["Parameters"] == ["stuff"]


@pytest.mark.parametrize("attach", ATTACHERS.values(), ids=ATTACHERS.keys())
def test_v2_query_carries_action(attach):
    plugin = _plugin_with_action(FlowLauncherV2(), attach)
    messages = [
        {"id": 1, "method": "query", "params": [{"search": "x", "trimmedQuery": "x"}, {}]},
        {"id": 2, "method": "close", "params": []},
    ]
    stdin_text = "\n".join(json.dumps(m) for m in messages) + "\n"

    async def dispatch(method, params):
        return await plugin._event_handler.trigger_event(method, *params)

    async def _run():
        with patch("sys.stdin", StringIO(stdin_text)), patch("sys.stdout", StringIO()) as out:
            await plugin._launcher.run(dispatch)
            return [json.loads(line) for line in out.getvalue().splitlines() if line.strip()]

    responses = asyncio.run(_run())
    reply = next(r for r in responses if r.get("id") == 1)
    action = reply["result"]["result"][0]["JsonRPCAction"]
    assert action["Method"] == "do_stuff"
    assert action["Parameters"] == ["stuff"]
