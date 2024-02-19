from pyflowlauncher.jsonrpc import server


def test_parse_request():
    assert server.parse_request('{"jsonrpc": "2.0", "method": "Test", "params": ["Test", false], "id": 1}') == {
        "jsonrpc": "2.0",
        "method": "Test",
        "params": ["Test", False],
        "id": 1,
    }


def test_create_response():
    assert server.create_response("Test", 1) == {
        "jsonrpc": "2.0",
        "result": "Test",
        "id": 1,
        "SettingsChange": None,
    }


def test_response():
    assert server.response("Test", 1) == '{"jsonrpc": "2.0", "result": "Test", "id": 1, "SettingsChange": null}'
