from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Union, cast

if sys.version_info < (3, 11):
    from typing_extensions import NotRequired, TypedDict
else:
    from typing import NotRequired, TypedDict

from .models.result import Glyph, PreviewInfo
from .models.json_rpc import JsonRPCResult, JsonRPCRequest, JsonRPCResponse



def action(method: Callable[..., Any], parameters: Optional[Iterable[Any]] = None, dont_hide_after_action: bool = False) -> JsonRPCRequest:
    """Creates a JsonRPCRequest for the given method and parameters."""
    return {
        'Method': method.__name__,
        'Parameters': list(parameters) if parameters else [],
        'DontHideAfterAction': dont_hide_after_action,
    }


@dataclass
class Result:
    title: str
    subtitle: Optional[str] = None
    icon: Optional[Union[str, Path]] = None
    score: int = 0
    json_rpc_action: Optional[JsonRPCRequest] = None
    context_data: Optional[Iterable] = None
    glyph: Optional[Glyph] = None
    copy_text: Optional[str] = None
    auto_complete_text: Optional[str] = None
    rounded_icon: bool = False
    preview: Optional[PreviewInfo] = None
    title_highlight_data: Optional[List[int]] = None

    def add_action(self, method: Callable[..., Any], parameters: Optional[Iterable[Any]] = None, dont_hide_after_action: bool = False) -> None:
        """Adds a JsonRPC action to the result."""
        self.json_rpc_action = {
            'Method': method.__name__,
            'Parameters': list(parameters) if parameters else [],
            'DontHideAfterAction': dont_hide_after_action,
        }

    def as_dict(self) -> Dict[str, Any]:
        return self.__dict__

    def to_json(self) -> JsonRPCResult:
        """Converts the Result instance to a JsonRPCResult dictionary"""
        return cast(JsonRPCResult, {
            'Title': self.title,
            'SubTitle': self.subtitle,
            'IcoPath': str(self.icon) if self.icon else None,
            'Score': self.score,
            'JsonRPCAction': self.json_rpc_action,
            'ContextData': self.context_data,
            'Glyph': self.glyph,
            'CopyText': self.copy_text,
            'AutoCompleteText': self.auto_complete_text,
            'RoundedIcon': self.rounded_icon,
            'Preview': self.preview,
            'TitleHighlightData': self.title_highlight_data,
        })


def send_results(results: Iterable[Result], settings: Optional[Dict[str, Any]] = None) -> JsonRPCResponse:
    """Formats and returns results as a JsonRPCResponse"""
    return {'Result': [result.to_json() for result in results], 'SettingsChange': settings}
