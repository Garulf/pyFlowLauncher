from typing import Optional
from .result import JsonRPCAction

NAME_SPACE = 'Flow.Launcher'


def _send_action(method: str, *parameters) -> JsonRPCAction:
    return {"method": f"{NAME_SPACE}.{method}", "parameters": parameters}


def change_query(query, requery=False) -> JsonRPCAction:
    """Change the query in Flow Launcher."""
    return _send_action("ChangeQuery", query, requery)


def shell_run(command: str, filename: str = 'cmd.exe') -> JsonRPCAction:
    """Run a shell command."""
    return _send_action("ShellRun", command, filename)


def close_app() -> JsonRPCAction:
    """Close Flow Launcher."""
    return _send_action("CloseApp")


def hide_app() -> JsonRPCAction:
    """Hide Flow Launcher."""
    return _send_action("HideApp")


def show_app() -> JsonRPCAction:
    """Show Flow Launcher."""
    return _send_action("ShowApp")


def show_msg(title, sub_title, ico_path="") -> JsonRPCAction:
    """Show a message in Flow Launcher."""
    return _send_action("ShowMsg", title, sub_title, ico_path)


def open_setting_dialog() -> JsonRPCAction:
    """Open the settings window in Flow Launcher."""
    return _send_action("OpenSettingDialog")


def start_loading_bar() -> JsonRPCAction:
    """Start the loading bar in Flow Launcher."""
    return _send_action("StartLoadingBar")


def stop_loading_bar() -> JsonRPCAction:
    """Stop the loading bar in Flow Launcher."""
    return _send_action("StopLoadingBar")


def reload_plugins() -> JsonRPCAction:
    """Reload the plugins in Flow Launcher."""
