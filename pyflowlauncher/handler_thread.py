"""Choose the thread a registered handler runs on."""
from __future__ import annotations

import asyncio
import functools
import inspect
from concurrent.futures import Executor
from typing import Any, Callable, Iterator, Optional, TypeVar

__all__ = ["OptionalExecutor", "call_handler", "main_thread"]

OptionalExecutor = Optional[Executor]

_MAIN_THREAD_ATTR = '_pyflowlauncher_main_thread'

F = TypeVar('F', bound=Callable[..., Any])


def main_thread(method: F) -> F:
    """Keep a handler on the main thread instead of the V2 worker thread.

    Use it for handlers that touch objects bound to the thread that created
    them, such as a sqlite3 connection opened at import time. Works before or
    after `@plugin.on_method`, and on bound methods.
    """
    setattr(getattr(method, '__func__', method), _MAIN_THREAD_ATTR, True)
    return method


def _wrapper_chain(fn: Callable[..., Any]) -> Iterator[Callable[..., Any]]:
    seen = set()
    current: Any = fn
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        yield current
        current = getattr(current, '__wrapped__', None)


def _runs_on_loop(handler: Callable[..., Any]) -> bool:
    return any(
        getattr(fn, _MAIN_THREAD_ATTR, False)
        or inspect.iscoroutinefunction(fn)
        or inspect.isasyncgenfunction(fn)
        for fn in _wrapper_chain(handler)
    )


async def call_handler(
    handler: Callable[..., Any], executor: Optional[Executor], *args: Any, **kwargs: Any,
) -> Any:
    """Call handler inline, or on executor when one is given and handler is sync."""
    if executor is None or _runs_on_loop(handler):
        return handler(*args, **kwargs)
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, functools.partial(handler, *args, **kwargs))
