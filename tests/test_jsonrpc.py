import sys
import pytest

from pyflowlauncher.jsonrpc import JsonRPCClient


@pytest.fixture
def capture_stdout(monkeypatch):
    buffer = {"stdout": "", "write_calls": 0}

    def fake_writes(s):
        buffer["stdout"] += s
        buffer["write_calls"] += 1

    monkeypatch.setattr(sys.stdout, "write", fake_writes)
    return buffer


def test_send(capture_stdout):
    jsonrpc = JsonRPCClient()
    jsonrpc.send({"method": "Test", "parameters": []})

    assert capture_stdout["stdout"] == '{"method": "Test", "parameters": []}'


def test_recieve(monkeypatch):
    jsonrpc = JsonRPCClient()

    monkeypatch.setattr(sys, "argv", ["test.py", '{"method": "Test", "parameters": []}'])
    assert jsonrpc.recieve() == {"method": "Test", "parameters": []}
