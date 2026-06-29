from __future__ import annotations

import asyncio
import json
import logging
import sys
from typing import Any, Mapping

if sys.version_info < (3, 11):
    from typing_extensions import NotRequired, TypedDict
else:
    from typing import NotRequired, TypedDict

_logger = logging.getLogger(__name__)


class JsonRPCRequest(TypedDict):
    method: str
    parameters: list
    settings: NotRequired[dict[Any, Any]]


class JsonRPCClient:

    def send(self, data: Mapping) -> None:
        json.dump(data, sys.stdout)

    def recieve(self) -> JsonRPCRequest:
        try:
            return json.loads(sys.argv[1])
        except (IndexError, json.JSONDecodeError):
            return {'method': 'query', 'parameters': ['']}


class JsonRPCV2Client:

    def __init__(self) -> None:
        self._pending: dict = {}
        self._counter: int = 0

    async def messages(self):
        """Async generator yielding parsed JSON-RPC request dicts from stdin.

        Responses to plugin-initiated calls (no 'method' key) are routed to
        their waiting Future and not yielded.
        """
        loop = asyncio.get_running_loop()
        while True:
            line = await loop.run_in_executor(None, sys.stdin.readline)
            if not line:
                return
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                _logger.warning("Bad JSON-RPC line: %r", line)
                continue
            if 'method' not in msg:
                req_id = msg.get('id')
                if req_id in self._pending:
                    fut = self._pending.pop(req_id)
                    if not fut.done():
                        fut.set_result(msg.get('result'))
                continue
            yield msg

    async def request(self, method: str, params: list) -> Any:
        """Send a JSON-RPC call to Flow Launcher and await the response."""
        self._counter += 1
        req_id = self._counter
        fut: asyncio.Future = asyncio.get_running_loop().create_future()
        self._pending[req_id] = fut
        self.send({'id': req_id, 'method': method, 'params': params})
        return await fut

    def send(self, data: dict) -> None:
        sys.stdout.write(json.dumps(data) + '\n')
        sys.stdout.flush()
