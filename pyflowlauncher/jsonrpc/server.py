from __future__ import annotations

import json
from typing import Any, Dict, Optional

from .models import JsonRPCRequest, JsonRPCResult, PartialJsonRPCResult

from . import JSONRPC_VER, ids


def parse_request(message: str) -> JsonRPCRequest:
    request = json.loads(message)
    if "id" not in request:
        request["id"] = next(ids)
    return request


def create_response(result: Any, SettingsChange: Optional[Dict] = None, id: Optional[int] = None) -> JsonRPCResult:
    return {
        "jsonrpc": JSONRPC_VER,
        "result": result,
        "SettingsChange": SettingsChange,
        "id": id,
    }


def response_string(result: Any, id: Optional[int] = None, SettingsChange: Optional[Dict] = None) -> str:
    return json.dumps(create_response(result, SettingsChange, id))


def response(result: Any, SettingsChange: Optional[Dict] = None) -> PartialJsonRPCResult:
    return {
        "result": result,
        "SettingsChange": SettingsChange
    }
