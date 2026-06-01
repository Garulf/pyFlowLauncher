from pyflowlauncher import Plugin, Result, send_results, api
from pyflowlauncher.models.json_rpc import JsonRPCResponse

plugin = Plugin()


@plugin.on_method
def query(query: str) -> JsonRPCResponse:
    r = Result(
        title="This is a title!",
        subtitle="This is the subtitle!",
        icon="icon.png",
        json_rpc_action=api.change_query("This is a new query!"),
    )
    return send_results([r])


plugin.run()
