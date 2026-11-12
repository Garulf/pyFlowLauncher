import os
import subprocess
import sys
import textwrap

import pytest

import pyflowlauncher
from pyflowlauncher import Plugin, Result
from pyflowlauncher.method import Method


class Query(Method):
    def __call__(self, query):
        self.add_result(Result(title=query))
        return self.return_results()


def test_constructing_a_method_warns():
    with pytest.warns(DeprecationWarning, match="on_method"):
        Query()


def test_warning_stays_off_stderr_in_a_plugin_script(tmp_path):
    """A V1 host fails any request whose process wrote to stderr."""
    script = tmp_path / "main.py"
    script.write_text(textwrap.dedent("""
        from pyflowlauncher import Method


        class Query(Method):
            def __call__(self, query):
                return self.return_results()


        Query()
    """))
    env = {k: v for k, v in os.environ.items() if k != "PYTHONWARNINGS"}

    done = subprocess.run(
        [sys.executable, str(script)], cwd=str(tmp_path), env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
    )

    assert done.returncode == 0
    assert done.stderr == ""


def test_method_is_still_exported():
    assert pyflowlauncher.Method is Method


def test_method_still_works_when_registered_by_name():
    plugin = Plugin()
    with pytest.warns(DeprecationWarning):
        instance = Query()

    plugin.add_method(instance, name="query")
    handler = plugin._event_handler.get_event("query")

    assert [r["Title"] for r in handler("a")["Result"]] == ["a"]
    assert [r["Title"] for r in handler("b")["Result"]] == ["b"]
