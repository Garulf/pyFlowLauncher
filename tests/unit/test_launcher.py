import asyncio
import json
import sys
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from pyflowlauncher.launcher import FlowLauncherV1, FlowLauncherV2, Launcher
from pyflowlauncher.plugin import Plugin
from pyflowlauncher.result import Result, send_results


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_dispatch(result=None):
    async def dispatch(method, params):
        return result
    return dispatch


def _make_dispatch_raising(exc):
    async def dispatch(method, params):
        raise exc
    return dispatch


def _v2_run(launcher, lines, dispatch=None):
    """Run FlowLauncherV2 with a fake stdin from a list of JSON-serialisable dicts."""
    dispatch = dispatch or _make_dispatch(None)
    stdin_text = '\n'.join(json.dumps(line) for line in lines) + '\n'

    async def _run():
        with patch('sys.stdin', StringIO(stdin_text)):
            await launcher.run(dispatch)

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# FlowLauncherV1
# ---------------------------------------------------------------------------

class TestFlowLauncherV1:

    def test_run_dispatches_and_sends(self, monkeypatch):
        launcher = FlowLauncherV1()
        request = {'method': 'query', 'parameters': ['hello'], 'settings': {}}
        sent = []
        monkeypatch.setattr(launcher._client, 'recieve', lambda: request)
        monkeypatch.setattr(launcher._client, 'send', lambda data: sent.append(data))

        result = send_results([Result(title='x')])
        asyncio.run(launcher.run(_make_dispatch(result)))

        assert sent == [result]

    def test_run_no_result_skips_send(self, monkeypatch):
        launcher = FlowLauncherV1()
        request = {'method': 'query', 'parameters': ['hello'], 'settings': {}}
        sent = []
        monkeypatch.setattr(launcher._client, 'recieve', lambda: request)
        monkeypatch.setattr(launcher._client, 'send', lambda data: sent.append(data))

        asyncio.run(launcher.run(_make_dispatch(None)))

        assert sent == []

    def test_settings_cached_after_run(self, monkeypatch):
        launcher = FlowLauncherV1()
        request = {'method': 'query', 'parameters': [], 'settings': {'key': 'value'}}
        monkeypatch.setattr(launcher._client, 'recieve', lambda: request)
        monkeypatch.setattr(launcher._client, 'send', lambda data: None)

        asyncio.run(launcher.run(_make_dispatch(None)))

        assert launcher.settings == {'key': 'value'}

    def test_is_default_for_unknown_manifest(self, monkeypatch):
        monkeypatch.setattr('pyflowlauncher.plugin.Plugin.manifest',
                            property(lambda self: (_ for _ in ()).throw(FileNotFoundError())),
                            raising=False)
        # patch cached_property by making root_dir raise
        with patch.object(Plugin, 'root_dir', new_callable=lambda: property(
            lambda self: (_ for _ in ()).throw(FileNotFoundError())
        )):
            plugin = Plugin()
        assert isinstance(plugin._launcher, FlowLauncherV1)

    def test_custom_launcher_injected(self):
        v2 = FlowLauncherV2()
        plugin = Plugin(launcher=v2)
        assert plugin._launcher is v2


# ---------------------------------------------------------------------------
# Auto-detection
# ---------------------------------------------------------------------------

class TestAutoDetect:

    def _plugin_with_language(self, language):
        manifest = MagicMock()
        manifest.language = language
        with patch.object(Plugin, 'manifest', new_callable=lambda: property(lambda self: manifest)):
            return Plugin()

    def test_auto_detect_v1(self):
        plugin = self._plugin_with_language('python')
        assert isinstance(plugin._launcher, FlowLauncherV1)

    def test_auto_detect_v2(self):
        plugin = self._plugin_with_language('python_v2')
        assert isinstance(plugin._launcher, FlowLauncherV2)

    def test_auto_detect_case_insensitive(self):
        plugin = self._plugin_with_language('Python_V2')
        assert isinstance(plugin._launcher, FlowLauncherV2)

    def test_explicit_overrides_auto_detect(self):
        manifest = MagicMock()
        manifest.language = 'python_v2'
        v1 = FlowLauncherV1()
        with patch.object(Plugin, 'manifest', new_callable=lambda: property(lambda self: manifest)):
            plugin = Plugin(launcher=v1)
        assert plugin._launcher is v1


# ---------------------------------------------------------------------------
# FlowLauncherV2
# ---------------------------------------------------------------------------

class TestFlowLauncherV2:

    def test_query_request_dispatches_search_string(self):
        launcher = FlowLauncherV2()
        received = []

        async def dispatch(method, params):
            received.append((method, params))
            return send_results([Result(title='x')])

        _v2_run(launcher, [
            {'id': 1, 'method': 'query', 'parameters': [{'search': 'hi', 'trimmedQuery': 'hi'}], 'settings': {}},
            {'id': 2, 'method': 'close', 'parameters': []},
        ], dispatch)

        assert received == [('query', ['hi'])]

    def test_response_echoes_id(self):
        launcher = FlowLauncherV2()
        output = []

        async def dispatch(method, params):
            return send_results([Result(title='r')])

        stdin_text = json.dumps({'id': 42, 'method': 'query',
                                 'parameters': [{'search': 'x'}], 'settings': {}}) + '\n'
        stdin_text += json.dumps({'id': 99, 'method': 'close', 'parameters': []}) + '\n'

        async def _run():
            with patch('sys.stdin', StringIO(stdin_text)), \
                 patch('sys.stdout', StringIO()) as mock_out:
                await launcher.run(dispatch)
                mock_out.seek(0)
                for line in mock_out.read().splitlines():
                    if line:
                        output.append(json.loads(line))

        asyncio.run(_run())

        query_resp = next(r for r in output if r.get('result') is not None)
        assert query_resp['id'] == 42

    def test_eof_exits_cleanly(self):
        launcher = FlowLauncherV2()
        _v2_run(launcher, [])  # empty stdin → EOF immediately

    def test_invalid_json_continues(self):
        launcher = FlowLauncherV2()
        received = []

        async def dispatch(method, params):
            received.append(method)
            return None

        stdin_io = StringIO('not-json\n' +
                            json.dumps({'id': 1, 'method': 'query',
                                        'parameters': [{'search': 'ok'}], 'settings': {}}) + '\n' +
                            json.dumps({'id': 2, 'method': 'close', 'parameters': []}) + '\n')

        async def _run():
            with patch('sys.stdin', stdin_io):
                await launcher.run(dispatch)

        asyncio.run(_run())
        assert received == ['query']

    def test_settings_cached_per_request(self):
        launcher = FlowLauncherV2()
        _v2_run(launcher, [
            {'id': 1, 'method': 'initialize', 'parameters': [], 'settings': {'k': 'v'}},
            {'id': 2, 'method': 'close', 'parameters': []},
        ])
        assert launcher.settings == {'k': 'v'}

    def test_lifecycle_initialize_not_dispatched(self):
        launcher = FlowLauncherV2()
        received = []

        async def dispatch(method, params):
            received.append(method)
            return None

        _v2_run(launcher, [
            {'id': 1, 'method': 'initialize', 'parameters': []},
            {'id': 2, 'method': 'close', 'parameters': []},
        ], dispatch)

        assert 'initialize' not in received

    def test_lifecycle_close_exits_loop(self):
        launcher = FlowLauncherV2()
        received = []

        async def dispatch(method, params):
            received.append(method)
            return None

        _v2_run(launcher, [
            {'id': 1, 'method': 'close', 'parameters': []},
            {'id': 2, 'method': 'query', 'parameters': [{'search': 'after_close'}]},
        ], dispatch)

        assert received == []

    def test_dispatch_exception_loop_continues(self):
        launcher = FlowLauncherV2()
        call_count = [0]

        async def dispatch(method, params):
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("boom")
            return None

        _v2_run(launcher, [
            {'id': 1, 'method': 'query', 'parameters': [{'search': 'a'}]},
            {'id': 2, 'method': 'query', 'parameters': [{'search': 'b'}]},
            {'id': 3, 'method': 'close', 'parameters': []},
        ], dispatch)

        assert call_count[0] == 2

    def test_action_response_has_hide(self):
        launcher = FlowLauncherV2()
        output = []

        async def dispatch(method, params):
            return {'Method': 'some_action', 'Parameters': []}

        stdin_text = json.dumps({'id': 5, 'method': 'on_click', 'parameters': [], 'settings': {}}) + '\n'
        stdin_text += json.dumps({'id': 6, 'method': 'close', 'parameters': []}) + '\n'

        async def _run():
            with patch('sys.stdin', StringIO(stdin_text)), \
                 patch('sys.stdout', StringIO()) as mock_out:
                await launcher.run(dispatch)
                mock_out.seek(0)
                for line in mock_out.read().splitlines():
                    if line:
                        output.append(json.loads(line))

        asyncio.run(_run())
        action_resp = next(r for r in output if 'hide' in r)
        assert action_resp == {'id': 5, 'hide': True}


# ---------------------------------------------------------------------------
# Launcher icons and program_dir
# ---------------------------------------------------------------------------

class TestLauncherIcons:

    def test_icons_return_path_when_program_dir_set(self, tmp_path):
        launcher = FlowLauncherV1.__new__(FlowLauncherV1)
        from pyflowlauncher.icons import Icons
        launcher.icons = Icons(tmp_path)
        assert launcher.icons.admin == str(tmp_path / 'Images' / 'admin.png')

    def test_icons_return_none_when_no_program_dir(self):
        from pyflowlauncher.icons import Icons
        icons = Icons(None)
        assert icons.admin is None

    def test_program_dir_from_env(self, tmp_path, monkeypatch):
        monkeypatch.setenv('FLOW_PROGRAM_DIRECTORY', str(tmp_path))
        launcher = FlowLauncherV1()
        assert launcher.program_dir == tmp_path
