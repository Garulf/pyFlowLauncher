from pyflowlauncher import api


def check_output(func, method, parameters):
    req = func(*parameters)
    assert req["method"] == method
    assert req["parameters"] == parameters


def test_get_namespace():
    assert api._get_namespace("Test") == "Flow.Launcher.Test"


def test_change_query():
    check_output(api.change_query, "Flow.Launcher.ChangeQuery", ["Test", False])


def test_shell_run():
    check_output(api.shell_run, "Flow.Launcher.ShellRun", ["Test", "Test"])


def test_close_app():
    check_output(api.close_app, "Flow.Launcher.CloseApp", [])


def test_hide_app():
    check_output(api.hide_app, "Flow.Launcher.HideApp", [])


def test_show_app():
    check_output(api.show_app, "Flow.Launcher.ShowApp", [])


def test_show_msg():
    check_output(api.show_msg, "Flow.Launcher.ShowMsg", ["Test", "Test", "Test"])


def test_open_setting_dialog():
    check_output(api.open_setting_dialog, "Flow.Launcher.OpenSettingDialog", [])


def test_start_loading_bar():
    check_output(api.start_loading_bar, "Flow.Launcher.StartLoadingBar", [])


def test_stop_loading_bar():
    check_output(api.stop_loading_bar, "Flow.Launcher.StopLoadingBar", [])


def test_reload_plugins():
    check_output(api.reload_plugins, "Flow.Launcher.ReloadPlugins", [])


def test_copy_to_clipboard():
    check_output(api.copy_to_clipboard, "Flow.Launcher.CopyToClipboard", ["Test", False, True])


def test_open_directory():
    check_output(api.open_directory, "Flow.Launcher.OpenDirectory", ["Test", "Test"])


def test_open_url():
    check_output(api.open_url, "Flow.Launcher.OpenUrl", ["Test", False])


def test_open_uri():
    check_output(api.open_uri, "Flow.Launcher.OpenUri", ["Test"])
