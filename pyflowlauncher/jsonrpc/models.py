from __future__ import annotations

import sys
from typing import Any, Dict, List, Optional

if sys.version_info < (3, 11):
    from typing_extensions import NotRequired, TypedDict
else:
    from typing import NotRequired, TypedDict


class BaseJsonRPCRequest(TypedDict):
    """Standard JsonRPC Request"""
    id: NotRequired[int]
    jsonrpc: NotRequired[str]
    method: str
    parameters: List


class JsonRPCRequest(BaseJsonRPCRequest):
    """Flow Launcher JsonRPC Request"""
    dontHideAfterAction: NotRequired[bool]
    settings: NotRequired[Dict]


class BaseJsonRPCResult(TypedDict):
    """Standard JsonRPC Result"""
    id: NotRequired[Optional[int]]
    jsonrpc: str
    result: Any


class JsonRPCResult(BaseJsonRPCResult):
    """Flow Launcher JsonRPC Result"""
    SettingsChange: NotRequired[Optional[Dict]]


class PartialJsonRPCResult(TypedDict):
    """Flow Launcher JsonRPC Result"""
    SettingsChange: NotRequired[Optional[Dict]]
    result: NotRequired[Dict]
