from __future__ import annotations

import functools
from typing import Any, Callable, Dict, Optional, Tuple

_registered: Dict[Callable[..., Any], str] = {}
# Unhashable callables (a class defining __eq__ without __hash__) are matched by identity.
_registered_unhashable: Dict[int, Tuple[Callable[..., Any], str]] = {}


def derive_name(method: Callable[..., Any]) -> str:
    """Return the RPC name a callable registers under when no name is given."""
    while isinstance(method, functools.partial):
        method = method.func
    name = getattr(method, '__name__', None)
    if not isinstance(name, str):
        name = type(method).__name__
    return name.lower()


def describe(method: Callable[..., Any]) -> str:
    name = getattr(method, '__name__', None)
    return name if isinstance(name, str) else repr(method)


def remember(method: Callable[..., Any], name: str) -> None:
    try:
        _registered[method] = name
    except TypeError:
        _registered_unhashable[id(method)] = (method, name)


def registered_name(method: Callable[..., Any]) -> Optional[str]:
    try:
        return _registered.get(method)
    except TypeError:
        entry = _registered_unhashable.get(id(method))
        return entry[1] if entry is not None and entry[0] is method else None
