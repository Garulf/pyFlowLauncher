from __future__ import annotations

import sys
from functools import wraps
from typing import Any, Callable, Iterable, Optional, Type, Union
from pathlib import Path
import json
import asyncio

from pyflowlauncher.shared import logger

from .event import EventHandler
from .jsonrpc import server
from .jsonrpc.models import JsonRPCRequest, JsonRPCResult
from .manifest import PluginManifestSchema, MANIFEST_FILE

Method = Callable[..., Union[JsonRPCResult, None]]


class Plugin:

    def __init__(self, methods: list[Method] | None = None) -> None:
        self._logger = logger(self)
        self._event_handler = EventHandler()
        self._settings: dict[str, Any] = {}
        if methods:
            self.add_methods(methods)

    def add_method(self, method: Method) -> str:
        """Add a method to the event handler."""
        return self._event_handler.add_event(method)

    def add_methods(self, methods: Iterable[Method]) -> None:
        self._event_handler.add_events(methods)

    def on_method(self, method: Method) -> Method:
        @wraps(method)
        def wrapper(*args, **kwargs):
            return method(*args, **kwargs)
        self._event_handler.add_event(wrapper)
        return wrapper

    def method(self, method: Method) -> Method:
        """Register a method to be called when the plugin is run."""
        return self.on_method(method)

    def add_exception_handler(self, exception: Type[Exception], handler: Callable[..., Any]) -> None:
        """Add exception handler to be called when an exception is raised in a method."""
        self._event_handler.add_exception_handler(exception, handler)

    def on_except(self, exception: Type[Exception]) -> Callable[..., Any]:
        @wraps(exception)
        def wrapper(handler: Callable[..., Any]) -> Callable[..., Any]:
            self.add_exception_handler(exception, handler)
            return handler
        return wrapper

    def action(self, method: Method, parameters: Optional[Iterable] = None) -> JsonRPCRequest:
        """Register a method and return a JsonRPCAction that calls it."""
        method_name = self.add_method(method)
        return {"method": method_name, "parameters": list(parameters or [])}

    async def run_async(self) -> None:
        request = server.parse_request(sys.argv[1])
        response = await self._event_handler.trigger_event(request["method"], *request["parameters"])
        print(server.response_string(**response, id=request["id"]))

    def run(self) -> None:
        if sys.version_info >= (3, 10, 0):
            asyncio.run(self.run_async())
        else:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.run_async())

    @property
    def run_dir(self) -> Path:
        """Return the run directory of the plugin."""
        return Path(sys.argv[0]).parent

    def root_dir(self) -> Path:
        """Return the root directory of the plugin."""
        current_dir = self.run_dir
        for part in current_dir.parts:
            if current_dir.joinpath(MANIFEST_FILE).exists():
                return current_dir
            current_dir = current_dir.parent
        raise FileNotFoundError(f"Could not find {MANIFEST_FILE} in {self.run_dir} or any parent directory.")

    def manifest(self) -> PluginManifestSchema:
        """Return the plugin manifest."""
        with open(self.root_dir() / MANIFEST_FILE, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        return manifest
