"""End-to-end tests for the V2 protocol across a real process boundary.

Flow Launcher keeps one plugin process alive and speaks newline-delimited
JSON-RPC over its stdin/stdout. These tests drive a real subprocess with the
exact message shapes the host sends (query params as objects, lifecycle
methods, $/ notifications) and assert on the raw response stream.
"""
import json


def query_titles(response: dict) -> list:
    return [r['Title'] for r in response['result']['result']]


def test_initialize_then_query(v2_plugin):
    response = v2_plugin.request(1, 'initialize', [{}])
    assert response['result'] == {}
    assert response['error'] is None

    # The host sends the query as an object: [Query, Settings.Inner]
    response = v2_plugin.request(2, 'query', [{'search': 'hello', 'rawQuery': 'e2e hello'}, {}])
    assert query_titles(response) == ['echo: hello']


def test_persistent_process_serves_many_queries(v2_plugin):
    for i, term in enumerate(('one', 'two', 'three'), start=1):
        response = v2_plugin.request(i, 'query', [{'search': term}, {}])
        assert query_titles(response) == [f'echo: {term}']
    assert v2_plugin.proc.poll() is None


def test_settings_from_query_params(v2_plugin):
    settings = {'token': 'xyz', 'limit': 3}
    response = v2_plugin.request(1, 'query', [{'search': 'q'}, settings])
    subtitle = response['result']['result'][0]['SubTitle']
    assert json.loads(subtitle) == settings


def test_cancel_request_notification_is_ignored(v2_plugin):
    v2_plugin.send({'jsonrpc': '2.0', 'method': '$/cancelRequest', 'params': {'id': 99}})
    v2_plugin.assert_no_output()
    response = v2_plugin.request(2, 'query', [{'search': 'after-cancel'}, {}])
    assert query_titles(response) == ['echo: after-cancel']


def test_context_menu(v2_plugin):
    response = v2_plugin.request(1, 'context_menu', [['ctx-data']])
    assert query_titles(response) == ['context: ["ctx-data"]']


def test_unicode_roundtrip(v2_plugin):
    response = v2_plugin.request(1, 'query', [{'search': 'héllo ☃'}, {}])
    assert query_titles(response) == ['echo: héllo ☃']


def test_close_shuts_down_cleanly(v2_plugin):
    response = v2_plugin.request(1, 'close', [])
    assert response['result'] == {}
    assert v2_plugin.proc.wait(timeout=10) == 0


def test_malformed_line_does_not_kill_the_process(v2_plugin):
    v2_plugin.proc.stdin.write('this is not json\n')
    v2_plugin.proc.stdin.flush()
    response = v2_plugin.request(1, 'query', [{'search': 'still-alive'}, {}])
    assert query_titles(response) == ['echo: still-alive']
