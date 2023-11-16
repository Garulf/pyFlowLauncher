import logging


_logger = logging.getLogger(__name__)


class PyFlowLauncherObject:
    _logger = None

    def __init_subclass__(cls) -> None:
        cls._logger = logging.getLogger(f"{cls.__module__}.{cls.__name__}")
