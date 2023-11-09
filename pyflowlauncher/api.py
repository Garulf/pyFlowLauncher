from .jsonrpc import JsonRPCRequest

NAME_SPACE = 'Flow.Launcher'


def change_query(query: str, requery: bool = False) -> JsonRPCRequest:
    """Change the query in Flow Launcher."""
    return {"method": f"{NAME_SPACE}.ChangeQuery", "parameters": [query, requery]}


def shell_run(command: str) -> JsonRPCRequest:
    """Run a shell command."""
    return {"method": f"{NAME_SPACE}.ShellRun", "parameters": [command]}


def close_app() -> JsonRPCRequest:
    """Close Flow Launcher."""
    return {"method": f"{NAME_SPACE}.CloseApp", "parameters": []}


def hide_app() -> JsonRPCRequest:
    """Hide Flow Launcher."""
    return {"method": f"{NAME_SPACE}.HideApp", "parameters": []}


def show_app() -> JsonRPCRequest:
    """Show Flow Launcher."""
    return {"method": f"{NAME_SPACE}.ShowApp", "parameters": []}


def show_msg(title: str, sub_title: str, ico_path: str = "") -> JsonRPCRequest:
    """Show a message in Flow Launcher."""
    return {"method": f"{NAME_SPACE}.ShowMsg", "parameters": [title, sub_title, ico_path]}


def open_setting_dialog() -> JsonRPCRequest:
    """Open the settings window in Flow Launcher."""
    return {"method": f"{NAME_SPACE}.OpenSettingDialog", "parameters": []}


def start_loading_bar() -> JsonRPCRequest:
    """Start the loading bar in Flow Launcher."""
    return {"method": f"{NAME_SPACE}.StartLoadingBar", "parameters": []}


def stop_loading_bar() -> JsonRPCRequest:
    """Stop the loading bar in Flow Launcher."""
    return {"method": f"{NAME_SPACE}.StopLoadingBar", "parameters": []}


def reload_plugins() -> JsonRPCRequest:
    """Reload the plugins in Flow Launcher."""
    return {"method": f"{NAME_SPACE}.ReloadPlugins", "parameters": []}
