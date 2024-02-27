from jsonrpcserver import method, async_dispatch as dispatch


class Plugin:

    def __init__(self):
        self.methods = {}

    def on_method(self, func):
        self.methods[func.__name__] = func
        return func

    async def run(self):
        while True:
            request = await self.receive_request()
            response = await dispatch(request, methods=self.methods)
            await self.send_response(response)

    async def receive_request(self):
        pass

    async def send_response(self, response):
        pass

