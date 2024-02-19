from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .result import Result, send_results
from .shared import logger
from .jsonrpc.models import JsonRPCResult


class Method(ABC):

    def __init__(self) -> None:
        self._logger = logger(self)
        self._results: list[Result] = []

    def add_result(self, result: Result) -> None:
        self._results.append(result)

    def return_results(self) -> List[Dict[str, Any]]:
        return send_results(self._results)

    @abstractmethod
    def __call__(self, *args, **kwargs) -> Optional[JsonRPCResult]:
        pass
