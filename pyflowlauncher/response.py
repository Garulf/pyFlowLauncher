from __future__ import annotations

import inspect
import logging
from typing import Any, Generator, Optional, Union

from .command import Command
from .result import Result, send_results
from .models.json_rpc import JsonRPCRequest, JsonRPCResponse

_logger = logging.getLogger(__name__)


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
    Coroutines and async generators are returned as-is for the event loop to handle.
    """
    if result is None:
        return None
    if isinstance(result, Result):
        return send_results([result])
    if isinstance(result, list):
        return send_results(_filter_results(result))
    if inspect.isgenerator(result):
        return _collect_generator(result)
    return result


def _collect_item(item: Any) -> list[Result]:
    if isinstance(item, Result):
        return [item]
    if isinstance(item, list):
        return _filter_results(item)
    _logger.warning("Dropping non-Result item yielded from a generator: %r", item)
    return []


def _collect_generator(gen: Generator[Any, Any, Any]) -> Union[JsonRPCResponse, Command]:
    results = []
    command: Optional[Command] = None
    for item in gen:
        if isinstance(item, Command):
            command = item
            continue
        results.extend(_collect_item(item))
    if command is not None:
        return command
    return send_results(results)
