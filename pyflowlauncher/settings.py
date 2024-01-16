from typing import Any
from .jsonrpc import JsonRPCClient


def settings() -> dict[str, Any]:
    """Retrieve the settings from Flow Launcher."""
    return JsonRPCClient().recieve().get('settings', {})
