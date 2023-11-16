import os
import logging

from .plugin import Plugin, ResultResponse
from .result import Result, JsonRPCAction, send_results


import importlib.metadata


log_level = os.environ.get("FLOW_LAUNCHER_API_LOG_LEVEL", "INFO")

logger = logging.getLogger(__name__)


__version__ = importlib.metadata.version(__name__)


__all__ = [
    "Plugin",
    "ResultResponse",
    "send_results",
    "Result",
    "JsonRPCAction",
]


logging.basicConfig(
    level=log_level,
    format="%(asctime)s <%(name)s>[%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
