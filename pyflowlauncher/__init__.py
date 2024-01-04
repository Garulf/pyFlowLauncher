import importlib.metadata
import logging
import os

from .plugin import Plugin
from .result import JsonRPCAction, Result, send_results, ResultResponse
from .method import Method

log_level = os.environ.get("FLOW_LAUNCHER_API_LOG_LEVEL", "INFO")

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


logging.basicConfig(
    level=log_level,
    format="%(asctime)s <%(name)s>[%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
