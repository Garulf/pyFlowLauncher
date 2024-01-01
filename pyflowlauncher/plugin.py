from __future__ import annotations

import sys
from functools import wraps
from typing import Any, Callable, Iterable, Union
from pathlib import Path
import json

from pyflowlauncher.shared import logger

from .event import EventHandler
from .jsonrpc import JsonRPCClient
from .result import JsonRPCAction, ResultResponse
from .manifest import PluginManifestSchema, MANIFEST_FILE

Method = Callable[..., Union[ResultResponse, JsonRPCAction]]


class Plugin:

    def __init__(self, methods: list[Method] | None = None) -> None:
        self._logger = logger(self)
        self._client = JsonRPCClient()
        self._event_handler = EventHandler()
        self._settings: dict[str, Any] = {}
        if methods:
            self.add_methods(methods)

    def add_method(self, method: Method) -> None:
        """Add a method to the event handler."""
        name = getattr(method, '__name__', method.__class__.__name__).lower()
        self._logger.debug(f"Adding method: '{name}'")
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
    def settings(self) -> dict:
        if self._settings is None:
            self._settings = {}
        self._settings = self._client.recieve().get('settings', {})
        return self._settings

    def run(self) -> None:
        request = self._client.recieve()
        method = request.get('method')
        parameters = request.get('parameters', [])
        feedback = self._event_handler(method, *parameters)
        # Inject settings if changed
        if 'result' in feedback and self._settings is not None:
            feedback['SettingsChange'] = self.settings
        self._client.send(feedback)

    def plugin_root_dir(self) -> Path:
        """Return the root directory of the plugin."""
        return Path(sys.argv[0]).parent

    def manifest(self) -> PluginManifestSchema:
        """Return the plugin manifest."""
        with open(self.plugin_root_dir() / MANIFEST_FILE, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        return manifest
