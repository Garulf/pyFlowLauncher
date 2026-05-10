from typing import Any, Dict, List, NotRequired, Optional, TypedDict

from .result import Result


class JsonRPCRequest(TypedDict):
    Method: str
    Parameters: list
    DontHideAfterAction: NotRequired[bool]


class JsonRPCResponse(TypedDict):
    Result: List[Result]
    SettingsChange: NotRequired[Optional[Dict[str, Any]]]


class JsonRPCResult(Result):
    JsonRPCAction: NotRequired[JsonRPCRequest]
    SettingsChange: NotRequired[Dict[str, Any]]