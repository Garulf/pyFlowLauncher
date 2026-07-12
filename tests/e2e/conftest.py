"""Helpers for spawning fixture plugins as real subprocesses.

These tests exercise the exact process boundary Flow Launcher uses:
V1 plugins get one JSON-RPC request as argv[1] and answer on stdout in a
fresh process per request; V2 plugins are a single long-lived process
speaking newline-delimited JSON-RPC over stdin/stdout.
"""
from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any, Optional

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / 'fixtures'
V1_PLUGIN = FIXTURES / 'v1_plugin' / 'main.py'
V2_PLUGIN = FIXTURES / 'v2_plugin' / 'main.py'

READ_TIMEOUT = 15.0


def plugin_env() -> dict:
    """Subprocess environment with the repo importable even without install."""
    env = os.environ.copy()
    env['PYTHONPATH'] = str(REPO_ROOT) + os.pathsep + env.get('PYTHONPATH', '')
    return env


@pytest.fixture
def run_v1(tmp_path):
    """Spawn the V1 fixture exactly as Flow Launcher does: fresh process,
    request JSON in argv[1], response read from stdout."""
    def _run(request: dict) -> str:
        completed = subprocess.run(
            [sys.executable, str(V1_PLUGIN), json.dumps(request)],
            capture_output=True, text=True, encoding='utf-8',
            cwd=tmp_path, env=plugin_env(), timeout=READ_TIMEOUT,
        )
        assert completed.returncode == 0, completed.stderr
        return completed.stdout
    return _run


class V2PluginProcess:
    """A persistent V2 plugin subprocess with a line-reader thread so tests
    never block forever on a plugin that stops responding."""

    def __init__(self, tmp_path: Path) -> None:
        self.proc = subprocess.Popen(
            [sys.executable, str(V2_PLUGIN)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding='utf-8', bufsize=1,
            cwd=tmp_path, env=plugin_env(),
        )
        self._lines: queue.Queue = queue.Queue()
        self._reader = threading.Thread(target=self._pump, daemon=True)
        self._reader.start()

    def _pump(self) -> None:
        for line in self.proc.stdout:
            if line.strip():
                self._lines.put(line)

    def send(self, message: dict) -> None:
        self.proc.stdin.write(json.dumps(message) + '\n')
        self.proc.stdin.flush()

    def read_message(self, timeout: float = READ_TIMEOUT) -> dict:
        try:
            return json.loads(self._lines.get(timeout=timeout))
        except queue.Empty:
            raise AssertionError(
                f"No response from V2 plugin within {timeout}s; "
                f"stderr: {self._drain_stderr()}"
            )

    def request(self, request_id: int, method: str, params: Optional[list] = None,
                **extra: Any) -> dict:
        """Send a request and return the response bearing the same id."""
        message = {'jsonrpc': '2.0', 'id': request_id, 'method': method,
                   'params': params or [], **extra}
        self.send(message)
        response = self.read_message()
        assert response.get('id') == request_id, (
            f"Expected response to id={request_id}, got: {response}")
        return response

    def assert_no_output(self, wait: float = 0.5) -> None:
        try:
            line = self._lines.get(timeout=wait)
        except queue.Empty:
            return
        raise AssertionError(f"Expected silence, but plugin wrote: {line!r}")

    def _drain_stderr(self) -> str:
        if self.proc.poll() is None:
            return '<process still running>'
        return self.proc.stderr.read()

    def close(self) -> None:
        if self.proc.poll() is None:
            self.proc.kill()
        self.proc.wait(timeout=5)
        for stream in (self.proc.stdin, self.proc.stdout, self.proc.stderr):
            if stream:
                stream.close()


@pytest.fixture
def v2_plugin(tmp_path):
    process = V2PluginProcess(tmp_path)
    yield process
    process.close()
