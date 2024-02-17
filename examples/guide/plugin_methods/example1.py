from pyflowlauncher import Plugin, Result, send_results
from pyflowlauncher.result import ResultResponse

plugin = Plugin()


@plugin.on_method
def query(query: str) -> ResultResponse:
    r = Result(
        Title="This is a title!",
        SubTitle="This is the subtitle!",
        JsonRPCAction={"method": "action", "parameters": []}
    )
    return send_results([r])


@plugin.on_method
def action(params: list[str]):
    pass
    # Do stuff here
    # ...


plugin.run()
