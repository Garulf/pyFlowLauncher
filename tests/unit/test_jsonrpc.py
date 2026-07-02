import asyncio
import logging
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


def test_v2_messages_routes_response_to_pending_future():
    """A message without 'method' resolves the matching pending Future."""
    resolved = []

    async def _run():
        client = JsonRPCV2Client()
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        client._pending[99] = fut

        stdin_text = '{"id": 99, "result": {"success": true}}\n'
        with patch('sys.stdin', StringIO(stdin_text)):
            async for _ in client.messages():
                pass

        resolved.append(await asyncio.wait_for(fut, timeout=1))

    asyncio.run(_run())
    assert resolved == [{"success": True}]


def test_v2_request_sends_correct_json(capture_stdout):
    async def _run():
        client = JsonRPCV2Client()
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        fut.set_result(None)
        client._pending[1] = fut
        client.send({'id': 1, 'method': 'FuzzySearch', 'params': ['hi', 'Hello']})

    asyncio.run(_run())
    assert '"method": "FuzzySearch"' in capture_stdout["stdout"]


def test_v2_request_times_out_when_no_response():
    """A lost response must not hang the caller forever."""
    async def _run():
        client = JsonRPCV2Client()
        with patch('sys.stdout', StringIO()):
            with pytest.raises(asyncio.TimeoutError):
                await client.request('FuzzySearch', ['a', 'b'], timeout=0.01)
        assert client._pending == {}

    asyncio.run(_run())


def test_v2_eof_fails_pending_futures():
    """Stream EOF must fail pending futures instead of leaving them hanging."""
    async def _run():
        client = JsonRPCV2Client()
        fut = asyncio.get_running_loop().create_future()
        client._pending[1] = fut

        with patch('sys.stdin', StringIO('')):
            async for _ in client.messages():
                pass

        with pytest.raises(ConnectionError):
            await asyncio.wait_for(fut, timeout=1)
        assert client._pending == {}

    asyncio.run(_run())


def test_v2_unmatched_response_id_logs_warning(caplog):
    """Responses with an unknown id must be logged, not silently dropped."""
    with caplog.at_level(logging.WARNING, logger='pyflowlauncher.jsonrpc'):
        msgs = _collect_messages('{"id": 7, "result": {}}\n')
    assert msgs == []
    assert any('7' in record.getMessage() for record in caplog.records)


def test_v2_request_resolves_on_response():
    """request() sends a call and resolves when the response arrives via messages()."""
    result = []

    async def _run():
        client = JsonRPCV2Client()
        # The request() writes to stdout then awaits; feed the response via stdin.
        stdin_text = '{"id": 1, "result": {"success": true, "score": 80}}\n'

        with patch('sys.stdin', StringIO(stdin_text)), \
             patch('sys.stdout', StringIO()):
            # Drain messages() concurrently so the response gets routed.
            async def drain():
                async for _ in client.messages():
                    pass

            task = asyncio.create_task(drain())
            val = await client.request('FuzzySearch', ['hi', 'Hello'])
            result.append(val)
            await task

    asyncio.run(_run())
    assert result == [{"success": True, "score": 80}]
