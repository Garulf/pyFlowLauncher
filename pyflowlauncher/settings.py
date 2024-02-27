import sys
from typing import Any, Dict

from .jsonrpc.server import parse_request


def settings() -> Dict[str, Any]:
    """Retrieve the settings from Flow Launcher."""
    request = parse_request(sys.argv[1])
    return request.get("settings", {})
