from pyflowlauncher import Plugin, Result, send_results, api
from pyflowlauncher.models.json_rpc import JsonRPCResponse

plugin = Plugin()


@plugin.on_method
def example_method() -> JsonRPCResponse:
    # Do stuff here
    return api.change_query("This is also a new query!")


@plugin.on_method
def query(query: str) -> JsonRPCResponse:
    r = Result(
        title="This is a title!",
        subtitle="This is the subtitle!",
        icon="icon.png",
    )
    r.add_action(example_method)
    return send_results([r])


plugin.run()
