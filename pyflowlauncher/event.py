import asyncio
from typing import Any, Callable, Iterable, Type


class EventHandler:

    def __init__(self):
        self._events = {}
        self._handlers = {}

    def _get_callable_name(self, method: Callable[..., Any]):
        return getattr(method, '__name__', method.__class__.__name__).lower()

    def add_event(self, event: Callable[..., Any], *, name=None) -> str:
        key = name or self._get_callable_name(event)
        self._events[key] = event
        return key

    def add_events(self, events: Iterable[Callable[..., Any]]):
        for event in events:
            self.add_event(event)

    def add_exception_handler(self, exception: Type[Exception], handler: Callable[..., Any]):
        self._handlers[exception] = handler

    def get_event(self, event: str) -> Callable[..., Any]:
        return self._events[event]

    async def _await_maybe(self, result: Any) -> Any:
        if asyncio.iscoroutine(result):
            return await result
        return result

    async def trigger_event(self, event: str, *args, **kwargs) -> Any:
        try:
            result = self.get_event(event)(*args, **kwargs)
            return await self._await_maybe(result)
        except Exception as e:
            handler = self._handlers.get(type(e), None)
            if handler:
                return handler(e)
            raise e
