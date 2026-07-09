import asyncio
import inspect

import pytest

from pyflowlauncher import api


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


def test_api_class_exposes_every_module_level_action():
    """Guard: each public module-level API function must exist on Api."""
    module_functions = [
        name for name, obj in vars(api).items()
        if inspect.isfunction(obj)
        and not name.startswith('_')
        and obj.__module__ == api.__name__
    ]
    missing = [name for name in module_functions if not hasattr(api.Api, name)]
    assert not missing, f"Api class is missing module-level actions: {missing}"
