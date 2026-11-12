"""On V2, sync handlers run on one worker thread so the loop keeps reading stdin."""

import asyncio
import json
import queue
import threading
from typing import Any, Dict, List
from unittest.mock import patch

import pytest

from pyflowlauncher import Plugin, Result, main_thread
from pyflowlauncher.launcher import FlowLauncherV2

TIMEOUT = 5.0


class _HostPipe:
    """Stands in for Flow Launcher: stdin lines the test feeds, stdout lines it reads."""

    def __init__(self) -> None:
        self._stdin: "queue.Queue[str]" = queue.Queue()
        self._replies: "queue.Queue[Dict[str, Any]]" = queue.Queue()
        self._buffer = ''
        self.seen: List[Dict[str, Any]] = []

    def send(self, message: dict) -> None:
        self._stdin.put(json.dumps(message) + '\n')

    def close_stdin(self) -> None:
        self._stdin.put('')

    def readline(self) -> str:
        return self._stdin.get(timeout=TIMEOUT)

    def write(self, text: str) -> int:
        self._buffer += text
        while '\n' in self._buffer:
            line, self._buffer = self._buffer.split('\n', 1)
            if line.strip():
                self._replies.put(json.loads(line))
        return len(text)

    def flush(self) -> None:
        pass

    def reply(self, request_id: Any) -> Dict[str, Any]:
        for msg in self.seen:
            if msg.get('id') == request_id:
                return msg
        while True:
            msg = self._replies.get(timeout=TIMEOUT)
            self.seen.append(msg)
            if msg.get('id') == request_id:
                return msg

    def drain(self) -> List[Dict[str, Any]]:
        while not self._replies.empty():
            self.seen.append(self._replies.get_nowait())
        return self.seen


def run_plugin(plugin: Plugin, script) -> _HostPipe:
    """Run plugin.run() on this thread while `script(host)` drives it from another."""
    host = _HostPipe()
    errors: List[BaseException] = []

    def drive() -> None:
        try:
            script(host)
        except BaseException as exc:
            errors.append(exc)
        finally:
            host.close_stdin()

    driver = threading.Thread(target=drive)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        with patch('sys.stdin', host), patch('sys.stdout', host):
            driver.start()
            plugin.run()
    finally:
        loop.close()
        asyncio.set_event_loop(None)
    driver.join(TIMEOUT)
    if errors:
        raise errors[0]
    host.drain()
    return host


def query_request(request_id: int, search: str) -> dict:
    return {'id': request_id, 'method': 'query', 'params': [{'search': search}, {}]}


def cancel_request(request_id: int) -> dict:
    return {'method': '$/cancelRequest', 'params': {'id': request_id}}


def titles(reply: dict) -> List[str]:
    return [r['Title'] for r in reply['result']['result']]


def test_cancel_is_read_while_sync_handler_runs():
    plugin = Plugin(launcher=FlowLauncherV2())
    started = threading.Event()
    release = threading.Event()
    finished = threading.Event()

    def query_handler(q: str):
        if q == 'slow':
            started.set()
            assert release.wait(TIMEOUT)
            finished.set()
        yield Result(title=q)

    plugin.add_method(query_handler, name='query')

    def script(host: _HostPipe) -> None:
        host.send(query_request(1, 'slow'))
        assert started.wait(TIMEOUT)
        host.send(cancel_request(1))
        cancelled = host.reply(1)
        assert not finished.is_set()
        assert 'result' not in cancelled
        assert cancelled['error']['code'] == -32800
        release.set()
        host.send(query_request(2, 'fresh'))
        assert titles(host.reply(2)) == ['fresh']
        host.send({'id': 3, 'method': 'close', 'params': []})

    host = run_plugin(plugin, script)
    assert finished.is_set()
    assert len([m for m in host.seen if m.get('id') == 1]) == 1


def test_queued_handler_never_starts_when_cancelled():
    plugin = Plugin(launcher=FlowLauncherV2())
    started = threading.Event()
    release = threading.Event()
    calls: List[str] = []

    def handler(q: str):
        calls.append(q)
        if q == 'first':
            started.set()
            assert release.wait(TIMEOUT)
        return [Result(title=q)]

    plugin.add_method(handler, name='query')

    def script(host: _HostPipe) -> None:
        host.send(query_request(1, 'first'))
        assert started.wait(TIMEOUT)
        host.send(query_request(2, 'queued'))
        host.send(cancel_request(2))
        assert host.reply(2)['error']['code'] == -32800
        release.set()
        assert titles(host.reply(1)) == ['first']
        host.send(query_request(3, 'later'))
        assert titles(host.reply(3)) == ['later']
        host.send({'id': 4, 'method': 'close', 'params': []})

    run_plugin(plugin, script)
    assert calls == ['first', 'later']


def test_handlers_never_overlap():
    plugin = Plugin(launcher=FlowLauncherV2())
    first_started = threading.Event()
    release = threading.Event()
    active: List[str] = []
    overlaps: List[List[str]] = []

    def handler(q: str):
        active.append(q)
        if len(active) > 1:
            overlaps.append(list(active))
        if q == 'a':
            first_started.set()
            assert release.wait(TIMEOUT)
        active.remove(q)
        return [Result(title=q)]

    plugin.add_method(handler, name='query')

    def script(host: _HostPipe) -> None:
        host.send(query_request(1, 'a'))
        assert first_started.wait(TIMEOUT)
        host.send(query_request(2, 'b'))
        release.set()
        assert titles(host.reply(1)) == ['a']
        assert titles(host.reply(2)) == ['b']
        host.send({'id': 3, 'method': 'close', 'params': []})

    run_plugin(plugin, script)
    assert overlaps == []


def _thread_of(plugin: Plugin, handler_name: str) -> threading.Thread:
    seen: List[threading.Thread] = []

    def script(host: _HostPipe) -> None:
        host.send({'id': 1, 'method': handler_name, 'params': [[]]})
        host.reply(1)
        host.send({'id': 2, 'method': 'close', 'params': []})

    run_plugin(plugin, script)
    seen.extend(getattr(plugin, 'threads_seen'))
    assert len(seen) == 1
    return seen[0]


def _recording_plugin() -> Plugin:
    plugin = Plugin(launcher=FlowLauncherV2())
    setattr(plugin, 'threads_seen', [])
    return plugin


def _record(plugin: Plugin) -> None:
    getattr(plugin, 'threads_seen').append(threading.current_thread())


def test_sync_generator_body_runs_on_worker_thread():
    plugin = _recording_plugin()

    @plugin.on_method
    def gen():
        yield Result(title='before')
        _record(plugin)
        yield Result(title='after')

    thread = _thread_of(plugin, 'gen')
    assert thread is not threading.main_thread()


def test_async_handler_runs_on_loop_thread():
    plugin = _recording_plugin()

    @plugin.on_method
    async def coro():
        _record(plugin)
        return [Result(title='async')]

    assert _thread_of(plugin, 'coro') is threading.main_thread()


def test_async_generator_handler_runs_on_loop_thread():
    plugin = _recording_plugin()

    @plugin.on_method
    async def agen():
        _record(plugin)
        yield Result(title='async gen')

    assert _thread_of(plugin, 'agen') is threading.main_thread()


def test_main_thread_marker_applied_before_registration():
    plugin = _recording_plugin()

    @plugin.on_method
    @main_thread
    def pinned():
        _record(plugin)
        yield Result(title='main')

    assert _thread_of(plugin, 'pinned') is threading.main_thread()


def test_main_thread_marker_applied_after_registration():
    plugin = _recording_plugin()

    @main_thread
    @plugin.on_method
    def pinned():
        _record(plugin)
        yield Result(title='main')

    assert _thread_of(plugin, 'pinned') is threading.main_thread()


class _Store:

    def __init__(self, plugin: Plugin) -> None:
        self.plugin = plugin

    @main_thread
    def marked_on_class(self):
        _record(self.plugin)
        return [Result(title='method')]

    def marked_later(self):
        _record(self.plugin)
        return [Result(title='method')]

    def unmarked(self):
        _record(self.plugin)
        return [Result(title='method')]


def _register_bound(plugin: Plugin, method: Any, name: str) -> None:
    # Plugin.add_method cannot register a bound method on main yet (it sets an
    # attribute on the callable), so register the same wraps() wrapper it builds.
    from functools import wraps
    from pyflowlauncher.response import handle_response

    @wraps(method)
    def wrapper(*args, **kwargs):
        return handle_response(method(*args, **kwargs))
    plugin._event_handler.add_event(wrapper, name=name)


def test_main_thread_on_bound_method_marked_in_class():
    plugin = _recording_plugin()
    _register_bound(plugin, _Store(plugin).marked_on_class, 'm')
    assert _thread_of(plugin, 'm') is threading.main_thread()


def test_main_thread_on_bound_method_marked_after_registration():
    plugin = _recording_plugin()
    store = _Store(plugin)
    _register_bound(plugin, store.marked_later, 'm')
    main_thread(store.marked_later)
    assert _thread_of(plugin, 'm') is threading.main_thread()


def test_unmarked_bound_method_runs_on_worker():
    plugin = _recording_plugin()
    _register_bound(plugin, _Store(plugin).unmarked, 'm')
    assert _thread_of(plugin, 'm') is not threading.main_thread()


def test_exception_on_worker_reaches_on_except():
    plugin = Plugin(launcher=FlowLauncherV2())
    raised_on: List[threading.Thread] = []

    @plugin.on_method
    def query(q: str):
        raised_on.append(threading.current_thread())
        raise ValueError(q)
        yield

    @plugin.on_except(ValueError)
    def handle(exc: ValueError):
        return [Result(title=f'handled {exc}')]

    def script(host: _HostPipe) -> None:
        host.send(query_request(1, 'boom'))
        assert titles(host.reply(1)) == ['handled boom']
        host.send({'id': 2, 'method': 'close', 'params': []})

    run_plugin(plugin, script)
    assert raised_on and raised_on[0] is not threading.main_thread()


@pytest.mark.parametrize('end', ['close', 'eof'])
def test_shutdown_waits_for_in_flight_handler_and_releases_worker(end):
    plugin = Plugin(launcher=FlowLauncherV2())
    started = threading.Event()
    release = threading.Event()
    worker: List[threading.Thread] = []

    @plugin.on_method
    def query(q: str):
        worker.append(threading.current_thread())
        started.set()
        assert release.wait(TIMEOUT)
        return [Result(title=q)]

    def script(host: _HostPipe) -> None:
        host.send(query_request(1, 'pending'))
        assert started.wait(TIMEOUT)
        if end == 'close':
            host.send({'id': 2, 'method': 'close', 'params': []})
        else:
            host.close_stdin()
        release.set()

    host = run_plugin(plugin, script)
    assert titles(host.reply(1)) == ['pending']
    worker[0].join(TIMEOUT)
    assert not worker[0].is_alive()
