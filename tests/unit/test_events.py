import pytest
from pyflowlauncher.event import EventHandler


def temp_method1():
    return None


def temp_method2():
    return None


async def async_temp_method3():
    return None


def except_method():
    raise Exception


class BaseError(Exception):
    pass


class SpecificError(BaseError):
    pass


def raise_specific_error():
    raise SpecificError


def test_add_method():
    handler = EventHandler()
    handler.add_event(temp_method1)
    assert handler._events == {"temp_method1": temp_method1}


def test_add_methods():
    handler = EventHandler()
    handler.add_events([temp_method1, temp_method2])
    assert handler._events == {"temp_method1": temp_method1, "temp_method2": temp_method2}


@pytest.mark.asyncio
async def test_call():
    handler = EventHandler()
    handler.add_event(temp_method1)
    assert await handler.trigger_event("temp_method1") is None


@pytest.mark.asyncio
async def test_call_async():
    handler = EventHandler()
    handler.add_event(async_temp_method3)
    assert await handler.trigger_event("async_temp_method3") is None


def test_add_exception_handler():
    handler = EventHandler()
    handler.add_exception_handler(Exception, temp_method1)
    assert handler._handlers == {Exception: temp_method1}


@pytest.mark.asyncio
async def test_call_exception():
    handler = EventHandler()
    handler.add_event(except_method)
    with pytest.raises(Exception):
        await handler.trigger_event("except_method")


@pytest.mark.asyncio
async def test_base_class_handler_catches_subclass():
    handler = EventHandler()
    handler.add_event(raise_specific_error)
    caught = []
    handler.add_exception_handler(BaseError, caught.append)
    await handler.trigger_event("raise_specific_error")
    assert len(caught) == 1
    assert isinstance(caught[0], SpecificError)


@pytest.mark.asyncio
async def test_most_specific_handler_wins_regardless_of_registration_order():
    handler = EventHandler()
    handler.add_event(raise_specific_error)
    base_calls = []
    specific_calls = []
    # Registered least-specific first - a naive isinstance loop over
    # self._handlers in insertion order would incorrectly match BaseError
    # here since it comes first and SpecificError is-a BaseError.
    handler.add_exception_handler(BaseError, base_calls.append)
    handler.add_exception_handler(SpecificError, specific_calls.append)

    await handler.trigger_event("raise_specific_error")

    assert len(specific_calls) == 1
    assert len(base_calls) == 0


@pytest.mark.asyncio
async def test_unhandled_subclass_reraises_when_no_ancestor_registered():
    handler = EventHandler()
    handler.add_event(raise_specific_error)
    handler.add_exception_handler(ValueError, lambda exc: None)

    with pytest.raises(SpecificError):
        await handler.trigger_event("raise_specific_error")
