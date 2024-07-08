from pyflowlauncher.jsonrpc import client


def test_create_request():
    assert client.create_request("Test", ["Test", False], id=1) == {
        "method": "Test", "parameters": ["Test", False], "id": 1, "jsonrpc": "2.0"}


def test_request_from_string():
    assert client.request_from_string(
        "Test", ["Test", False], id=1) == '{"jsonrpc": "2.0", "method": "Test", "parameters": ["Test", false], "id": 1}'


def test_send_request(capsys):
    client.send_request(client.create_request("Test", ["Test", False], id=1))
    captured = capsys.readouterr()
    assert captured.out == '{"jsonrpc": "2.0", "method": "Test", "parameters": ["Test", false], "id": 1}\n'
