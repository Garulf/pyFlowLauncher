from typing import Any, Dict, Iterable, Callable, Optional, TypedDict, Union
from functools import wraps

from .result import Result, JsonRPCAction
from .jsonrpc import JsonRPCClient
from .event import EventHandler


class ResultResponse(TypedDict):
    result: Iterable[Dict[str, Any]]


Method = Callable[..., Union[ResultResponse, JsonRPCAction]]


def send_results(results: Iterable[Result]) -> ResultResponse:
    return {'result': [result.as_dict() for result in results]}


class Plugin:

    def __init__(self, methods: Optional[list[Method]] = None) -> None:
        self._client = JsonRPCClient()
        self._event_handler = EventHandler()
        self._settings: Dict[str, Any] = {}
        if methods:
            self.add_methods(methods)

    def add_method(self, method: Method, *, name: Optional[str] = None) -> None:
        self._event_handler.add_method(method, name=name)

    def add_methods(self, methods: Iterable[Method]) -> None:
        self._event_handler.add_methods(methods)

    def on_method(self, method: Method) -> Method:
        @wraps(method)
        def wrapper(*args, **kwargs):
            return method(*args, **kwargs)
        self._event_handler.add_method(wrapper)
        return wrapper

    @property
    def settings(self) -> Dict:
        if self._settings is None:
            self._settings = {}
        self._settings = self._client.recieve().get('settings', {})
        return self._settings

    def run(self) -> None:
        request = self._client.recieve()
        method = request.get('method')
        parameters = request.get('parameters', [])
        feedback = self._event_handler(method, *parameters)
        self._client.send(feedback)
