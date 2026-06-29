import asyncio
import sys
from io import StringIO
from unittest.mock import patch

import pytest

from pyflowlauncher.jsonrpc import JsonRPCClient, JsonRPCV2Client


@pytest.fixture
def capture_stdout(monkeypatch):
    buffer = {"stdout": "", "write_calls": 0}

    def fake_writes(s):
        buffer["stdout"] += s
        buffer["write_calls"] += 1

    monkeypatch.setattr(sys.stdout, "write", fake_writes)
    return buffer


# ---------------------------------------------------------------------------
# JsonRPCClient (V1)
# ---------------------------------------------------------------------------

def test_send(capture_stdout):
    jsonrpc = JsonRPCClient()
    jsonrpc.send({"method": "Test", "parameters": []})

    assert capture_stdout["stdout"] == '{"method": "Test", "parameters": []}'


def test_recieve(monkeypatch):
    jsonrpc = JsonRPCClient()

    monkeypatch.setattr(sys, "argv", ["test.py", '{"method": "Test", "parameters": []}'])
    assert jsonrpc.recieve() == {"method": "Test", "parameters": []}


# ---------------------------------------------------------------------------
# JsonRPCV2Client
# ---------------------------------------------------------------------------

def _collect_messages(stdin_text):
    """Run JsonRPCV2Client.messages() against stdin_text; return yielded dicts."""
    results = []

    async def _run():
        client = JsonRPCV2Client()
        with patch('sys.stdin', StringIO(stdin_text)):
            async for msg in client.messages():
                results.append(msg)

    asyncio.run(_run())
    return results


def test_v2_send_newline_delimited(capture_stdout):
    client = JsonRPCV2Client()
    client.send({"id": 1, "result": {}})
    assert capture_stdout["stdout"] == '{"id": 1, "result": {}}\n'


def test_v2_messages_yields_parsed_dicts():
    msgs = _collect_messages('{"method": "query"}\n{"method": "close"}\n')
    assert msgs == [{"method": "query"}, {"method": "close"}]


def test_v2_messages_skips_invalid_json():
    msgs = _collect_messages('not-json\n{"method": "ok"}\n')
    assert msgs == [{"method": "ok"}]


def test_v2_messages_stops_on_eof():
    msgs = _collect_messages('')
    assert msgs == []


def test_v2_messages_skips_blank_lines():
    msgs = _collect_messages('\n{"method": "ping"}\n\n')
    assert msgs == [{"method": "ping"}]
