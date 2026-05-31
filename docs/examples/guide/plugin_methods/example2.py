from pyflowlauncher import Plugin, Result, send_results
from pyflowlauncher.models.json_rpc import JsonRPCResponse

plugin = Plugin()


@plugin.on_method
def query(query: str) -> JsonRPCResponse:
    r = Result(
        title="This is a title!",
        subtitle="This is the subtitle!",
    )
    r.add_action(action, ["stuff"])
    return send_results([r])


def action(params: list[str]):
    pass
    # Do stuff here
    # ...


plugin.run()
