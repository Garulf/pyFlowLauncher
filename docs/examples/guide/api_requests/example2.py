from pyflowlauncher import Plugin, Result, send_results, api
from pyflowlauncher.result import JsonRPCAction, ResultResponse

plugin = Plugin()


@plugin.on_method
def example_method() -> JsonRPCAction:
    # Do stuff here
    return api.change_query("This is also a new query!")


@plugin.on_method
def query(query: str) -> ResultResponse:
    r = Result(
        Title="This is a title!",
        SubTitle="This is the subtitle!",
        IcoPath="icon.png",
    )
    r.add_action(example_method)
    return send_results([r])


plugin.run()
