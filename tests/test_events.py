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


def test_add_method():
    handler = EventHandler()
    handler.add_method(temp_method1)
    assert handler._methods == {"temp_method1": temp_method1}


def test_add_methods():
    handler = EventHandler()
    handler.add_methods([temp_method1, temp_method2])
    assert handler._methods == {"temp_method1": temp_method1, "temp_method2": temp_method2}


@pytest.mark.asyncio
async def test_call():
    handler = EventHandler()
    handler.add_method(temp_method1)
    assert await handler("temp_method1") is None


@pytest.mark.asyncio
async def test_call_async():
    handler = EventHandler()
    handler.add_method(async_temp_method3)
    assert await handler("async_temp_method3") is None


def test_add_exception_handler():
    handler = EventHandler()
    handler.add_exception_handler(Exception, temp_method1)
    assert handler._handlers == {Exception: temp_method1}


@pytest.mark.asyncio
async def test_call_exception():
    handler = EventHandler()
    handler.add_method(except_method)
    with pytest.raises(Exception):
        await handler("except_method")
