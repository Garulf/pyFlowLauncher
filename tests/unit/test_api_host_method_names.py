import asyncio
import warnings

import pytest

from pyflowlauncher import api
from pyflowlauncher.launcher import FlowLauncherV2

# Method names declared on Flow Launcher's IPublicAPI, which the V1 host
# resolves built-in actions against by reflection.
V1_HOST_METHODS = {
    "ChangeQuery", "RestartApp", "ShellRun", "CopyToClipboard", "SaveAppAllSettings",
    "SavePluginSettings", "ReloadAllPluginData", "CheckForNewUpdate", "ShowMsgError",
    "ShowMainWindow", "FocusQueryTextBox", "HideMainWindow", "IsMainWindowVisible",
    "ShowMsg", "OpenSettingDialog", "OpenPluginSettingsWindow", "GetTranslation",
    "FuzzySearch", "OpenDirectory", "OpenWebUrl", "OpenUrl", "OpenAppUri",
    "BackToQueryResults", "StartLoadingBar", "StopLoadingBar", "SavePluginCaches",
}

# Method names on the V2 host's JsonRPCPublicAPI target. StreamJsonRpc also
# answers to each "...Async" method without the suffix.
V2_HOST_METHODS = {
    "ChangeQuery", "RestartApp", "ShellRun", "CopyToClipboard", "SaveAppAllSettings",
    "SavePluginSettings", "ReloadAllPluginDataAsync", "ReloadAllPluginData",
    "CheckForNewUpdate", "ShowMsgError", "ShowMainWindow", "HideMainWindow",
    "IsMainWindowVisible", "ShowMsg", "OpenSettingDialog", "OpenPluginSettingsWindow",
    "GetTranslation", "FuzzySearch", "OpenDirectory", "OpenUrl", "OpenAppUri",
    "BackToQueryResults", "StartLoadingBar", "StopLoadingBar", "SavePluginCaches",
}

BUILDERS = [
    lambda: api.change_query("q"),
    lambda: api.shell_run("dir"),
    api.hide_app,
    api.show_app,
    lambda: api.show_msg("t", "s"),
    api.open_setting_dialog,
    api.start_loading_bar,
    api.stop_loading_bar,
    api.reload_plugins,
    lambda: api.copy_to_clipboard("x"),
    lambda: api.open_directory("C:/"),
    lambda: api.open_url("https://example.com"),
    lambda: api.open_uri("ms-settings:"),
]


def _bare_name(command):
    return command["Method"][len(f"{api.NAME_SPACE}."):]


@pytest.mark.parametrize("build", BUILDERS)
def test_builder_names_a_method_both_hosts_have(build):
    name = _bare_name(build())
    assert name in V1_HOST_METHODS
    assert name in V2_HOST_METHODS


def test_hide_app_targets_hide_main_window():
    assert api.hide_app() == {"Method": "Flow.Launcher.HideMainWindow", "Parameters": []}


def test_show_app_targets_show_main_window():
    assert api.show_app() == {"Method": "Flow.Launcher.ShowMainWindow", "Parameters": []}


def test_reload_plugins_targets_reload_all_plugin_data():
    assert api.reload_plugins() == {
        "Method": "Flow.Launcher.ReloadAllPluginData", "Parameters": []
    }


def test_v2_forwards_reload_plugins_under_a_name_the_host_answers():
    launcher = FlowLauncherV2()
    calls = []

    class FakeClient:
        async def request(self, method, params):
            calls.append(method)

    launcher._client = FakeClient()
    asyncio.run(launcher.api.invoke(api.reload_plugins()))
    assert calls == ["ReloadAllPluginData"]
    assert calls[0] in V2_HOST_METHODS


def test_close_app_warns_that_the_host_has_no_such_method():
    with pytest.warns(DeprecationWarning, match="no method") as record:
        command = api.close_app()
    assert record[0].filename == __file__
    assert command == {"Method": "Flow.Launcher.CloseApp", "Parameters": []}


def test_other_builders_do_not_warn():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        for build in BUILDERS:
            build()
