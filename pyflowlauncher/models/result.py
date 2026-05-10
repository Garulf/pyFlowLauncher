from typing import TypedDict, Optional, Iterable, Required, NotRequired


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


class Result(TypedDict, total=False):
    Title: Required[str]
    SubTitle: NotRequired[str]
    IcoPath: NotRequired[str]
    Score: NotRequired[int]
    ContextData: NotRequired[Iterable]
    Glyph: NotRequired[Glyph]
    CopyText: NotRequired[str]
    AutoCompleteText: NotRequired[str]
    RoundedIcon: NotRequired[bool]
    Preview: NotRequired[PreviewInfo]
    TitleHighlightData: NotRequired[Iterable[int]]