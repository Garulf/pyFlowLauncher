import json
import threading
from io import StringIO
from typing import List
from unittest.mock import patch

from pyflowlauncher import Plugin, Result
from pyflowlauncher.launcher import FlowLauncherV1


def test_v1_sync_handler_runs_on_main_thread():
    plugin = Plugin(launcher=FlowLauncherV1())
    threads: List[threading.Thread] = []

    @plugin.on_method
    def query(q: str):
        threads.append(threading.current_thread())
        yield Result(title=q)

    request = json.dumps({'method': 'query', 'parameters': ['hi'], 'settings': {}})
    with patch('sys.argv', ['main.py', request]), patch('sys.stdout', StringIO()) as out:
        plugin.run()

    assert threads == [threading.main_thread()]
    assert json.loads(out.getvalue())['Result'][0]['Title'] == 'hi'
    assert plugin.launcher.handler_executor is None
