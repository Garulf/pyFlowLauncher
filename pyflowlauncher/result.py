from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict, Any, Dict, Iterable, List, Optional, Union

from .jsonrpc.models import JsonRPCRequest
from .jsonrpc.client import create_request

if TYPE_CHECKING:
    from .plugin import Method


class Glyph(TypedDict):
    """Flow Launcher Glyph"""
    Glyph: str
    FontFamily: str


class PreviewInfo(TypedDict):
    """Flow Launcher Preview section"""
    PreviewImagePath: Optional[str]
    Description: Optional[str]
    IsMedia: bool
    PreviewDeligate: Optional[str]


@dataclass
class Result:
    Title: str
    SubTitle: Optional[str] = None
    IcoPath: Optional[Union[str, Path]] = None
    Score: int = 0
    JsonRPCAction: Optional[JsonRPCRequest] = None
    ContextData: Optional[Iterable] = None
    Glyph: Optional[Glyph] = None
    CopyText: Optional[str] = None
    AutoCompleteText: Optional[str] = None
    RoundedIcon: bool = False
    Preview: Optional[PreviewInfo] = None
    TitleHighlightData: Optional[List[int]] = None

    def as_dict(self) -> Dict[str, Any]:
        return self.__dict__

    def add_action(self, method: Method,
                   parameters: Optional[Iterable[Any]] = None,
                   *,
                   dont_hide_after_action: bool = False) -> None:
        self.JsonRPCAction = create_request(
            method.__name__,
            list(parameters or []),
        )
        self.JsonRPCAction["dontHideAfterAction"] = dont_hide_after_action


def send_results(results: Iterable[Result]) -> List[Dict[str, Any]]:
    """Formats and returns results as a JsonRPCResponse"""
    return [result.as_dict() for result in results]
