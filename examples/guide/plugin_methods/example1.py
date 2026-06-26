from pyflowlauncher import Plugin, Result

plugin = Plugin()


@plugin.on_method
def query(query: str):
    yield Result(
        title="This is a title!",
        subtitle="This is the subtitle!",
        json_rpc_action={"Method": "action", "Parameters": []}
    )


@plugin.on_method
def action(params: list[str]):
    pass
    # Do stuff here
    # ...


plugin.run()
