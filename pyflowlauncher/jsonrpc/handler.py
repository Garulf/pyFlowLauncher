import asyncio
import logging

from ..base import Base
from .models import JsonRPCRequest


_logger = logging.getLogger(__name__)


class Dispatcher(Base):

    def __init__(self):
        self._methods = {}

    def add_method(self, func):
        self._methods[func.__name__] = func
        _logger.debug(f"Adding method {func.__name__} to dispatcher")
        return func

    def remove_method(self, func):
        del self._methods[func.__name__]

    async def await_maybe(self, func):
        if asyncio.iscoroutine(func):
            return await func
        return func

    async def dispatch(self, request: JsonRPCRequest):
        method = self._methods.get(request['method'])
        if method is None:
            return {'error': 'method not found'}
        return await self.await_maybe(method(*request['parameters']))
