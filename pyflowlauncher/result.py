from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Union

if sys.version_info < (3, 11):
    from typing_extensions import NotRequired, TypedDict
else:
    from typing import NotRequired, TypedDict


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


class PreviewInfo(TypedDict):
    """Flow Launcher Preview section"""
    PreviewImagePath: Optional[str]
    Description: Optional[str]
    IsMedia: bool
    PreviewDeligate: Optional[str]


class Result(TypedDict):
    """Result Item"""
    Title: str
    SubTitle: NotRequired[str]
    IcoPath: NotRequired[Union[str, Path]]
    Score: NotRequired[int]
    JsonRPCAction: NotRequired[JsonRPCAction]
    ContextData: NotRequired[Iterable]
    Glyph: NotRequired[Glyph]
    CopyText: NotRequired[str]
    AutoCompleteText: NotRequired[str]
    RoundedIcon: NotRequired[bool]
    Preview: NotRequired[PreviewInfo]
    TitleHighlightData: NotRequired[List[int]]


class ResultResponse(TypedDict):
    result: List[Dict[str, Any]]
    SettingsChange: NotRequired[Optional[Dict[str, Any]]]


def create_result(
    title: str,
    sub_title: Optional[str] = None,
    ico_path: Optional[Union[str, Path]] = None,
    score: Optional[int] = None,
    jsonrpc_action: Optional[JsonRPCAction] = None,
    context_data: Optional[Iterable] = None,
    glyph: Optional[Glyph] = None,
    copy_text: Optional[str] = None,
    auto_complete_text: Optional[str] = None,
    rounded_icon: Optional[bool] = False,
    preview: Optional[PreviewInfo] = None,
    title_highlight_data: Optional[List[int]] = None
) -> Result:
    return {
        "Title": title,
        "SubTitle": sub_title,
        "IcoPath": ico_path,
        "Score": score,
        "JsonRPCAction": jsonrpc_action,
        "ContextData": context_data,
        "Glyph": glyph,
        "CopyText": copy_text,
        "AutoCompleteText": auto_complete_text,
        "RoundedIcon": rounded_icon,
        "Preview": preview,
        "TitleHighlightData": title_highlight_data
    }
