from __future__ import annotations

import warnings
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from .models.json_rpc import JsonRPCRequest, JsonRPCResponse
from .result import Result, send_results
from .base import pyFlowLauncherObject


class Method(pyFlowLauncherObject, ABC):
    """Deprecated. Register a plain function with ``@plugin.on_method`` instead."""

    def __new__(cls, *args: Any, **kwargs: Any) -> Method:
        warnings.warn(
            f"{cls.__name__} subclasses Method, which is deprecated. "
            "Use a plain function registered with @plugin.on_method instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return super().__new__(cls)

    def __init__(self) -> None:
        super().__init__()
        self._results: list[Result] = []

    def add_result(self, result: Result) -> None:
        self._results.append(result)

    def return_results(self, settings: Optional[Dict[str, Any]] = None) -> JsonRPCResponse:
        results, self._results = self._results, []
        return send_results(results, settings)

    @abstractmethod
    def __call__(self, *args, **kwargs) -> JsonRPCResponse | JsonRPCRequest:
        pass
