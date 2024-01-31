import importlib.metadata
import logging

from .plugin import Plugin
from .result import JsonRPCAction, Result, send_results, ResultResponse
from .method import Method


logger = logging.getLogger(__name__)


__version__ = importlib.metadata.version(__name__)


__all__ = [
    "Plugin",
    "ResultResponse",
    "send_results",
    "Result",
    "JsonRPCAction",
    "Method",
]
