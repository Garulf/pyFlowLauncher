from pyflowlauncher import Plugin, Result

plugin = Plugin()


@plugin.on_method
def query(query: str):
    r = Result(
        title="This is a title!",
        subtitle="This is the subtitle!",
    )
    r.add_action(action, ["stuff"])
    yield r


def action(params: list[str]):
    pass
    # Do stuff here
    # ...


plugin.run()
