from pyflowlauncher import Plugin, Result, send_results, api
from pyflowlauncher.result import ResultResponse

plugin = Plugin()


@plugin.on_method
def query(query: str) -> ResultResponse:
    r = Result(
        Title="This is a title!",
        SubTitle="This is the subtitle!",
        IcoPath="icon.png",
        JsonRPCAction=api.change_query("This is a new query!"),
    )
    return send_results([r])


plugin.run()
