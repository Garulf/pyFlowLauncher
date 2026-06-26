from pyflowlauncher import Plugin, Result, send_results
from pyflowlauncher.models.json_rpc import JsonRPCResponse
from pyflowlauncher.icons import ADMIN

plugin = Plugin()


@plugin.on_method
def query(query: str) -> JsonRPCResponse:
    r = Result(
        title="This is a title!",
        subtitle="This is the subtitle!",
        icon=ADMIN
    )
    return send_results([r])


plugin.run()
