

from typing import Any, Callable, Iterable


class EventHandler:

    def __init__(self):
        self._methods = {}
        self._handlers = {}

    def _get_callable_name(self, method: Callable[..., Any]):
        return getattr(method, '__name__', method.__class__.__name__).lower()

    def add_method(self, method: Callable[..., Any], *, name=None):
        self._methods[name or self._get_callable_name(method)] = method

    def add_methods(self, methods: Iterable[Callable[..., Any]]):
        for method in methods:
            self.add_method(method)

    def add_exception_handler(self, exception: Exception, handler: Callable[..., Any]):
        self._handlers[exception.__class__.__name__] = handler

    def __call__(self, method: str, *args, **kwargs):
        try:
            return self._methods[method](*args, **kwargs)
        except Exception as e:
            handler = self._handlers.get(e.__class__.__name__, None)
            if handler:
                return handler(e)
            raise e
