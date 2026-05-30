from pyflowlauncher import Plugin, Result, send_results
from pyflowlauncher.models.json_rpc import JsonRPCResponse

plugin = Plugin()


@plugin.on_method
def query(query: str) -> JsonRPCResponse:
    r = Result(
        title="This is a title!",
        subtitle="This is the subtitle!",
        json_rpc_action={"Method": "action", "Parameters": []}
    )
    return send_results([r])


@plugin.on_method
def action(params: list[str]):
    pass
    # Do stuff here
    # ...


plugin.run()
