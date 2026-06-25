import inspect
from typing import Any, Generator, Union

from .result import Result, send_results
from .models.json_rpc import JsonRPCRequest, JsonRPCResponse


def handle_response(result: Any) -> Union[JsonRPCResponse, JsonRPCRequest, None]:
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
        return send_results(result)
    if inspect.isgenerator(result):
        return _collect_generator(result)
    return result


def _collect_generator(gen: Generator) -> JsonRPCResponse:
    results = []
    for item in gen:
        if isinstance(item, Result):
            results.append(item)
        elif isinstance(item, list):
            results.extend(r for r in item if isinstance(r, Result))
    return send_results(results)
