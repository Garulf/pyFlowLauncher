from __future__ import annotations

import json
from typing import Any, Dict, Optional

from .models import JsonRPCRequest, JsonRPCResult

from . import JSONRPC_VER, ids


def parse_request(message: str) -> JsonRPCRequest:
    request = json.loads(message)
    if "id" not in request:
        request["id"] = next(ids)
    return request


def create_response(result: Any, id: int, SettingsChange: Optional[Dict] = None) -> JsonRPCResult:
    return {
        "jsonrpc": JSONRPC_VER,
        "result": result,
        "id": id,
        "SettingsChange": SettingsChange
    }


def response(result: Any, id: int, SettingsChange: Optional[Dict] = None) -> str:
    return json.dumps(create_response(result, id, SettingsChange))
