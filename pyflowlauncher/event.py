

from typing import Any, Callable


class EventHandler:

    def __init__(self):
        self._methods = {}
        self._handlers = {}

    def add_method(self, method, *, name=None):
        self._methods[name or method.__name__] = method

    def add_methods(self, methods):
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
