import os
import logging

from pathlib import Path
from typing import Dict, Optional


_logger = logging.getLogger(__name__)

IMAGE_DIR = "Images"
FLOW_PROGRAM_DIRECTORY = os.getenv("FLOW_PROGRAM_DIRECTORY", None)

ENV_EXISTS: bool = FLOW_PROGRAM_DIRECTORY is not None

if not ENV_EXISTS:
    _logger.warning("Unable to find FLOW_PROGRAM_DIRECTORY environment variable. Icons will not be loaded.")


def _get_icon(icon_name: str, file_ext: str = "png") -> Optional[str]:
    if ENV_EXISTS:
        return str(Path(FLOW_PROGRAM_DIRECTORY) / IMAGE_DIR / f"{icon_name}.{file_ext}")  # type: ignore
    return None
