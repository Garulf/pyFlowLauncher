import asyncio

import pytest

from pyflowlauncher import api
from pyflowlauncher.command import Command


def test_builder_returns_command_equal_to_plain_dict():
    cmd = api.change_query("Test", False)
    assert isinstance(cmd, Command)
    assert cmd == {"Method": "Flow.Launcher.ChangeQuery", "Parameters": ["Test", False]}


def test_api_instance_builder_matches_module_builder():
    assert api.Api().change_query("Test") == api.change_query("Test")


def test_send_action():
    assert api._send_action("Test", "Test") == {"Method": "Flow.Launcher.Test", "Parameters": ["Test"]}


def test_change_query():
    assert api.change_query("Test", False) == {"Method": "Flow.Launcher.ChangeQuery", "Parameters": ["Test", False]}


def test_shell_run():
    assert api.shell_run("Test", "Test") == {"Method": "Flow.Launcher.ShellRun", "Parameters": ["Test", "Test"]}


def test_close_app():
    assert api.close_app() == {"Method": "Flow.Launcher.CloseApp", "Parameters": []}


def test_hide_app():
    assert api.hide_app() == {"Method": "Flow.Launcher.HideApp", "Parameters": []}


def test_show_app():
    assert api.show_app() == {"Method": "Flow.Launcher.ShowApp", "Parameters": []}


def test_show_msg():
    assert api.show_msg("Test", "Test", "Test") == {"Method": "Flow.Launcher.ShowMsg", "Parameters": ["Test", "Test", "Test"]}


def test_open_setting_dialog():
    assert api.open_setting_dialog() == {"Method": "Flow.Launcher.OpenSettingDialog", "Parameters": []}


def test_start_loading_bar():
    assert api.start_loading_bar() == {"Method": "Flow.Launcher.StartLoadingBar", "Parameters": []}


def test_stop_loading_bar():
    assert api.stop_loading_bar() == {"Method": "Flow.Launcher.StopLoadingBar", "Parameters": []}


def test_reload_plugins():
    assert api.reload_plugins() == {"Method": "Flow.Launcher.ReloadPlugins", "Parameters": []}


def test_copy_to_clipboard():
    assert api.copy_to_clipboard("Test", False, True) == {"Method": "Flow.Launcher.CopyToClipboard", "Parameters": ["Test", False, True]}


def test_open_directory():
    assert api.open_directory("Test", "Test") == {"Method": "Flow.Launcher.OpenDirectory", "Parameters": ["Test", "Test"]}


def test_open_url():
    assert api.open_url("Test", False) == {"Method": "Flow.Launcher.OpenUrl", "Parameters": ["Test", False]}


def test_open_uri():
    assert api.open_uri("Test") == {"Method": "Flow.Launcher.OpenAppUri", "Parameters": ["Test"]}


def test_fuzzy_search_without_backend_raises_clear_error():
    bare_api = api.Api()
    with pytest.raises(RuntimeError, match="fuzzy_search"):
        asyncio.run(bare_api.fuzzy_search("query", "text"))


def test_module_level_builders_resolve_to_api_methods():
    """Guard: every BC module-level builder is the Api method of the same name."""
    names = [
        "change_query", "shell_run", "close_app", "hide_app", "show_app",
        "show_msg", "open_setting_dialog", "start_loading_bar", "stop_loading_bar",
        "reload_plugins", "copy_to_clipboard", "open_directory", "open_url", "open_uri",
    ]
    for name in names:
        assert hasattr(api.Api, name), f"Api is missing builder: {name}"
        assert getattr(api, name).__func__ is getattr(api.Api, name)
