from __future__ import annotations

import asyncio
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Awaitable, Callable, Optional

from .api import Api
from .base import pyFlowLauncherObject
from .icons import Icons
from .jsonrpc import JsonRPCClient, JsonRPCV2Client
from .models.json_rpc import MatchResult
from .string_matcher import MatchData, string_matcher as _local_string_matcher


class Launcher(pyFlowLauncherObject, ABC):

    def __init__(self) -> None:
        super().__init__()
        self._settings: dict = {}
        self.api = Api(fuzzy_search_fn=self._fuzzy_search)
        self._program_dir: Optional[Path] = self._find_program_dir()
        self.icons = Icons(self._program_dir)

    async def _fuzzy_search(self, query: str, text: str) -> MatchData:
        """Local fallback matcher; subclasses may delegate to the host."""
        return _local_string_matcher(query, text)

    @property
    def settings(self) -> dict:
        return self._settings

    @property
    def program_dir(self) -> Optional[Path]:
        return self._program_dir

    def _find_program_dir(self) -> Optional[Path]:
        env = os.getenv("FLOW_PROGRAM_DIRECTORY")
        if env:
            return Path(env)
        appdata = os.getenv("APPDATA")
        if appdata:
            candidate = Path(appdata) / "FlowLauncher"
            if candidate.exists():
                return candidate
        local = os.getenv("LOCALAPPDATA")
        if local:
            candidate = Path(local) / "FlowLauncher"
            if candidate.exists():
                return candidate
        current = Path.cwd()
        for _ in range(5):
            if (current / "Flow.Launcher.exe").exists():
                return current
            current = current.parent
        self.logger.warning("Could not locate Flow Launcher program directory.")
        return None

    @abstractmethod
    async def run(self, dispatch: Callable[[str, list], Awaitable[Any]]) -> None: ...


class FlowLauncherV1(Launcher):

    def __init__(self) -> None:
        super().__init__()
        self._client = JsonRPCClient()

    async def run(self, dispatch: Callable[[str, list], Awaitable[Any]]) -> None:
        request = self._client.recieve()
        self._settings = request.get('settings', {})
        result = await dispatch(request['method'], request.get('parameters', []))
        if result:
            self._client.send(result)


class FlowLauncherV2(Launcher):

    _LIFECYCLE_METHODS = {'initialize', 'reload_data'}

    def __init__(self) -> None:
        super().__init__()
        self._client = JsonRPCV2Client()

    async def _fuzzy_search(self, query: str, text: str) -> MatchData:
        """Delegate to Flow Launcher's FuzzySearch over JSON-RPC."""
        result: MatchResult = await self._client.request('FuzzySearch', [query, text])
        return MatchData(
            matched=result.get('success', False),
            score_cutoff=result.get('searchPrecision', 50),
            index_list=result.get('matchData') or [],
            score=result.get('score', 0),
        )

    async def run(self, dispatch: Callable[[str, list], Awaitable[Any]]) -> None:
        tasks: set = set()
        async for request in self._client.messages():
            request_id = request.get('id')
            method = request.get('method', '')
            incoming_settings = request.get('settings')
            if incoming_settings is not None:
                self._settings = incoming_settings

            if method == 'close':
                self._respond(request_id, {})
                break

            if method in self._LIFECYCLE_METHODS:
                self._respond(request_id, {})
                continue

            if method.startswith('$/'):
                continue

            params = request.get('params', request.get('parameters', []))
            if method == 'query' and params and isinstance(params[0], dict):
                params = [params[0].get('search') or params[0].get('trimmedQuery', '')]

            task = asyncio.create_task(
                self._handle_request(request_id, method, params, dispatch)
            )
            tasks.add(task)
            task.add_done_callback(tasks.discard)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _handle_request(
        self,
        request_id: Any,
        method: str,
        params: list,
        dispatch: Callable[[str, list], Awaitable[Any]],
    ) -> None:
        try:
            result = await dispatch(method, params)
        except Exception:
            self.logger.exception("Unhandled error dispatching %r", method)
            self._respond(request_id, {
                'result': [], 'debugMessage': 'Internal error', 'settingsChange': None,
            })
            return
        self._send_response(request_id, method, result)

    def _respond(self, request_id: Any, result: Any) -> None:
        """Send a response in the uniform {id, result, error} envelope."""
        self._client.send({'id': request_id, 'result': result, 'error': None})

    def _send_response(self, request_id: Any, method: str, result: Any) -> None:
        if result is None:
            self._respond(request_id, {})
        elif isinstance(result, dict) and 'Result' in result:
            self._respond(request_id, {
                'result': result['Result'],
                'settingsChange': result.get('SettingsChange'),
                'debugMessage': '',
            })
        else:
            # Actions: StreamJsonRpc deserializes the result member as
            # JsonRPCExecuteResponse, whose 'hide' controls window hiding.
            self._respond(request_id, {'hide': True})
