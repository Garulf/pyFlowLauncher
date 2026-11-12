from __future__ import annotations

import inspect
import logging
from typing import Any, Iterable, List, Optional, Union

from .command import Command
from .result import Result, send_results
from .models.json_rpc import JsonRPCRequest, JsonRPCResponse

_logger = logging.getLogger(__name__)


class CommandWithResults(Command):
    """A Command yielded alongside Results.

    Behaves as the Command everywhere a Command is expected, so V1 still writes
    it as the response; ``results`` keeps what a V2 query reply can still show.
    """

    def __init__(self, command: Command, results: List[Result]) -> None:
        super().__init__(command)
        self.results = results


def _filter_results(items: list) -> list[Result]:
    results = []
    for item in items:
        if isinstance(item, Result):
            results.append(item)
        else:
            _logger.warning("Dropping non-Result item from response list: %r", item)
    return results


def handle_response(result: Any) -> Union[JsonRPCResponse, JsonRPCRequest, Command, None]:
    """Normalize a method's return value into a JSON-RPC response.

    Accepts: Result, list of Result, generator of Result/list, JsonRPCRequest,
    JsonRPCResponse, coroutine, async generator, or None.
    Coroutines and async generators are returned as-is; use ``normalize`` to
    await them.
    """
    if result is None:
        return None
    if isinstance(result, Result):
        return send_results([result])
    if isinstance(result, list):
        return send_results(_filter_results(result))
    if inspect.isgenerator(result):
        return _collect_items(result)
    return result


async def normalize(result: Any) -> Union[JsonRPCResponse, JsonRPCRequest, Command, None]:
    """Await a handler's output and normalize it with ``handle_response``."""
    while inspect.iscoroutine(result):
        result = await result
    if inspect.isasyncgen(result):
        return _collect_items([item async for item in result])
    return handle_response(result)


def _collect_item(item: Any) -> list[Result]:
    if isinstance(item, Result):
        return [item]
    if isinstance(item, list):
        return _filter_results(item)
    _logger.warning("Dropping non-Result item yielded from a generator: %r", item)
    return []


def _collect_items(items: Iterable[Any]) -> Union[JsonRPCResponse, Command]:
    results: list[Result] = []
    command: Optional[Command] = None
    for item in items:
        if isinstance(item, Command):
            command = item
            continue
        results.extend(_collect_item(item))
    if command is not None:
        return CommandWithResults(command, results)
    return send_results(results)
