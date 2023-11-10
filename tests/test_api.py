from pyflowlauncher import api


def test_send_action():
    assert api._send_action("Test", "Test") == {"method": "Flow.Launcher.Test", "parameters": ("Test",)}


def test_change_query():
    assert api.change_query("Test", False) == {"method": "Flow.Launcher.ChangeQuery", "parameters": ("Test", False)}


def test_shell_run():
    assert api.shell_run("Test", "Test") == {"method": "Flow.Launcher.ShellRun", "parameters": ("Test", "Test")}


def test_close_app():
    assert api.close_app() == {"method": "Flow.Launcher.CloseApp", "parameters": ()}


def test_hide_app():
    assert api.hide_app() == {"method": "Flow.Launcher.HideApp", "parameters": ()}


def test_show_app():
    assert api.show_app() == {"method": "Flow.Launcher.ShowApp", "parameters": ()}


def test_show_msg():
    assert api.show_msg("Test", "Test", "Test") == {"method": "Flow.Launcher.ShowMsg", "parameters": ("Test", "Test", "Test")}


def test_open_setting_dialog():
    assert api.open_setting_dialog() == {"method": "Flow.Launcher.OpenSettingDialog", "parameters": ()}


def test_start_loading_bar():
    assert api.start_loading_bar() == {"method": "Flow.Launcher.StartLoadingBar", "parameters": ()}


def test_stop_loading_bar():
    assert api.stop_loading_bar() == {"method": "Flow.Launcher.StopLoadingBar", "parameters": ()}


def test_reload_plugins():
    assert api.reload_plugins() == {"method": "Flow.Launcher.ReloadPlugins", "parameters": ()}


def test_copy_to_clipboard():
    assert api.copy_to_clipboard("Test", False, True) == {"method": "Flow.Launcher.CopyToClipboard", "parameters": ("Test", False, True)}


def test_open_directory():
    assert api.open_directory("Test", "Test") == {"method": "Flow.Launcher.OpenDirectory", "parameters": ("Test", "Test")}


def test_open_url():
    assert api.open_url("Test", False) == {"method": "Flow.Launcher.OpenUrl", "parameters": ("Test", False)}


def test_open_uri():
    assert api.open_uri("Test") == {"method": "Flow.Launcher.OpenAppUri", "parameters": ("Test",)}
