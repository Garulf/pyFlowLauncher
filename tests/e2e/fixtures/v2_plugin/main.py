"""Fixture plugin spawned as a real subprocess by the e2e tests (V2 protocol)."""
import json

from pyflowlauncher import Plugin, Result

plugin = Plugin()


@plugin.on_method
def query(q: str):
    yield Result(
        title=f"echo: {q}",
        subtitle=json.dumps(plugin.settings),
        icon="icon.png",
    )


@plugin.on_method
def context_menu(data):
    yield Result(title=f"context: {json.dumps(data)}")


if __name__ == '__main__':
    plugin.run()
