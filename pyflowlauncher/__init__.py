import os
import logging
import sys

from .plugin import Plugin, ResultResponse
from .result import Result, JsonRPCAction, send_results

if sys.version_info < (3, 8):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata


log_level = os.environ.get("FLOW_LAUNCHER_API_LOG_LEVEL", "INFO")

logger = logging.getLogger(__name__)


__version__ = importlib_metadata.version(__name__)


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
