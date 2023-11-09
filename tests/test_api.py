from pyflowlauncher import api


def test_change_query():
    assert api.change_query("Test") == {"method": "Flow.Launcher.ChangeQuery", "parameters": ["Test", False]}


def test_shell_run():
    assert api.shell_run("Test") == {"method": "Flow.Launcher.ShellRun", "parameters": ["Test"]}


def test_close_app():
    assert api.close_app() == {"method": "Flow.Launcher.CloseApp", "parameters": []}


def test_hide_app():
    assert api.hide_app() == {"method": "Flow.Launcher.HideApp", "parameters": []}


def test_show_app():
    assert api.show_app() == {"method": "Flow.Launcher.ShowApp", "parameters": []}


def test_show_msg():
    assert api.show_msg("Test", "Test", "Test") == {"method": "Flow.Launcher.ShowMsg", "parameters": ["Test", "Test", "Test"]}
