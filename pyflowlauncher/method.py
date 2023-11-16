from __future__ import annotations
from typing import Any, Iterable, TypedDict
from abc import ABC, abstractmethod

from .result import Result, JsonRPCAction, send_results
from .shared import logger


class ResultResponse(TypedDict):
    result: Iterable[dict[str, Any]]


class Method(ABC):

    def __init__(self) -> None:
        self._logger = logger(self)
        self._results: list[Result] = []

    def add_result(self, result: Result) -> None:
        self._results.append(result)

    def return_results(self) -> ResultResponse:
        return send_results(self._results)

    @abstractmethod
    def __call__(self, *args, **kwargs) -> ResultResponse | JsonRPCAction:
        pass
