from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Iterable,
    Optional,
    TypedDict,
    Union,
    Dict,
    NotRequired
)


if TYPE_CHECKING:
    from .plugin import Method


class JsonRPCAction(TypedDict):
    """Flow Launcher JsonRPCAction"""
    method: str
    parameters: Iterable
    dontHideAfterAction: NotRequired[bool]


class Glyph(TypedDict):
    """Flow Launcher Glyph"""
    Glyph: str
    FontFamily: str


@dataclass
class Result:
    Title: str
    SubTitle: Optional[str] = None
    IcoPath: Optional[Union[str, Path]] = None
    Score: int = 0
    JsonRPCAction: Optional[JsonRPCAction] = None
    ContextData: Optional[Iterable] = None
    Glyph: Optional[Glyph] = None
    CopyText: Optional[str] = None
    AutoCompleteText: Optional[str] = None
    RoundedIcon: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return self.__dict__

    def add_action(self, method: Method,
                   parameters: Optional[Iterable[Any]] = None,
                   *,
                   dont_hide_after_action: bool = False) -> None:
        self.JsonRPCAction = {
            "method": method.__name__,
            "parameters": parameters or [],
            "dontHideAfterAction": dont_hide_after_action
        }
