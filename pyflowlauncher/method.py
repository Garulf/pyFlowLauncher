from typing import Any, Dict, Iterable, List, TypedDict
from abc import ABC, abstractmethod


from pyflowlauncher.result import Result, JsonRPCAction
from .shared import PyFlowLauncherObject


class ResultResponse(TypedDict):
    result: Iterable[Dict[str, Any]]


class Method(ABC, PyFlowLauncherObject):

    def __init__(self) -> None:
        self._results: List[Result] = []

    def add_result(self, result: Result) -> None:
        self._results.append(result)

    def return_results(self) -> ResultResponse:
        return {'result': [result.as_dict() for result in self._results]}

    @abstractmethod
    def __call__(self, *args, **kwargs) -> ResultResponse | JsonRPCAction:
        pass
