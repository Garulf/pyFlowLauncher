from abc import ABC
import logging


_logger = logging.getLogger(__name__)


class Base(ABC):

    _LOGGER = _logger.getChild("Base")

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__).getChild(self.__class__.__name__)

    def __del__(self):
        self._logger.debug(f"Destroying {self.__class__.__name__} instance")
