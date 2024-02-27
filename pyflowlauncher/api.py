from typing import Optional

from .jsonrpc.models import JsonRPCRequest
from .jsonrpc.client import create_request

NAME_SPACE = 'Flow.Launcher'


def _get_namespace(method: str) -> str:
    return f"{NAME_SPACE}.{method}"


def change_query(query: str, requery: bool = False) -> JsonRPCRequest:
    """Change the query in Flow Launcher."""
    return create_request(_get_namespace("ChangeQuery"), [query, requery])


def shell_run(command: str, filename: str = 'cmd.exe') -> JsonRPCRequest:
    """Run a shell command."""
    return create_request(_get_namespace("ShellRun"), [command, filename])


def close_app() -> JsonRPCRequest:
    """Close Flow Launcher."""
    return create_request(_get_namespace("CloseApp"))


def hide_app() -> JsonRPCRequest:
    """Hide Flow Launcher."""
    return create_request(_get_namespace("HideApp"))


def show_app() -> JsonRPCRequest:
    """Show Flow Launcher."""
    return create_request(_get_namespace("ShowApp"))


def show_msg(title: str, sub_title: str, ico_path: str = "") -> JsonRPCRequest:
    """Show a message in Flow Launcher."""
    return create_request(_get_namespace("ShowMsg"), [title, sub_title, ico_path])


def open_setting_dialog() -> JsonRPCRequest:
    """Open the settings window in Flow Launcher."""
    return create_request(_get_namespace("OpenSettingDialog"))


def start_loading_bar() -> JsonRPCRequest:
    """Start the loading bar in Flow Launcher."""
    return create_request(_get_namespace("StartLoadingBar"))


def stop_loading_bar() -> JsonRPCRequest:
    """Stop the loading bar in Flow Launcher."""
    return create_request(_get_namespace("StopLoadingBar"))


def reload_plugins() -> JsonRPCRequest:
    """Reload the plugins in Flow Launcher."""
    return create_request(_get_namespace("ReloadPlugins"))


def copy_to_clipboard(text: str, direct_copy: bool = False, show_default_notification=True) -> JsonRPCRequest:
    """Copy text to the clipboard."""
    return create_request(_get_namespace("CopyToClipboard"), [text, direct_copy, show_default_notification])


def open_directory(directory_path: str, filename_or_filepath: Optional[str] = None) -> JsonRPCRequest:
    """Open a directory."""
    return create_request(_get_namespace("OpenDirectory"), [directory_path, filename_or_filepath])


def open_url(url: str, in_private: bool = False) -> JsonRPCRequest:
    """Open a URL."""
    return create_request(_get_namespace("OpenUrl"), [url, in_private])


def open_uri(uri: str) -> JsonRPCRequest:
    """Open a URI."""
    return create_request(_get_namespace("OpenUri"), [uri])
