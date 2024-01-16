from pyflowlauncher import Plugin, Result, send_results
from pyflowlauncher.result import ResultResponse
from pyflowlauncher.icons import ADMIN

plugin = Plugin()


@plugin.on_method
def query(query: str) -> ResultResponse:
    r = Result(
        Title="This is a title!",
        SubTitle="This is the subtitle!",
        IcoPath=ADMIN
    )
    return send_results([r])


plugin.run()