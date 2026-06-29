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

    async def messages(self):
        """Async generator yielding parsed JSON-RPC dicts read from stdin."""
        loop = asyncio.get_event_loop()
        while True:
            line = await loop.run_in_executor(None, sys.stdin.readline)
            if not line:
                return
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                _logger.warning("Bad JSON-RPC line: %r", line)

    def send(self, data: dict) -> None:
        sys.stdout.write(json.dumps(data) + '\n')
        sys.stdout.flush()
