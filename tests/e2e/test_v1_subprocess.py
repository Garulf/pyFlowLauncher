"""End-to-end tests for the V1 protocol across a real process boundary.

Flow Launcher spawns a fresh process per request with the JSON-RPC request
serialized into argv[1] and deserializes whatever the process writes to
stdout. These tests do exactly that — they catch buffering, encoding, and
stream-pollution bugs that in-process tests with patched stdio cannot.
"""
import json


def test_query_roundtrip(run_v1):
    stdout = run_v1({'method': 'query', 'parameters': ['hello'], 'settings': {}})
    response = json.loads(stdout)
    assert response['Result'][0]['Title'] == 'echo: hello'


def test_stdout_is_pure_json(run_v1):
    """Nothing (logging, warnings, prints) may pollute the response stream."""
    stdout = run_v1({'method': 'query', 'parameters': ['x'], 'settings': {}})
    json.loads(stdout)


def test_settings_reach_the_plugin(run_v1):
    settings = {'api_key': 'abc123', 'max_results': 5}
    stdout = run_v1({'method': 'query', 'parameters': ['q'], 'settings': settings})
    response = json.loads(stdout)
    assert json.loads(response['Result'][0]['SubTitle']) == settings


def test_unicode_query(run_v1):
    stdout = run_v1({'method': 'query', 'parameters': ['héllo ☃'], 'settings': {}})
    response = json.loads(stdout)
    assert response['Result'][0]['Title'] == 'echo: héllo ☃'


def test_context_menu(run_v1):
    stdout = run_v1({'method': 'context_menu', 'parameters': [['ctx-data']], 'settings': {}})
    response = json.loads(stdout)
    assert response['Result'][0]['Title'] == 'context: ["ctx-data"]'


def test_empty_query(run_v1):
    stdout = run_v1({'method': 'query', 'parameters': [''], 'settings': {}})
    response = json.loads(stdout)
    assert response['Result'][0]['Title'] == 'echo: '
