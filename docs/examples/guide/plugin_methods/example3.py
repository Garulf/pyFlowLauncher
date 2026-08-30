from pyflowlauncher import Plugin, Result

plugin = Plugin()


@plugin.on_method
def query(query: str):
    yield Result(
        title="This is a title!",
        subtitle="Right-click me for a context menu.",
        context_data=[
            Result(title="This is a context menu item!"),
            Result(title="So is this!"),
        ],
    )


plugin.run()
