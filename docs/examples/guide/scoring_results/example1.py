from pyflowlauncher import Plugin, Result
from pyflowlauncher.utils import score_results

plugin = Plugin()


@plugin.on_method
def query(query: str):
    results = [
        Result(
            title="This is a title!",
            subtitle="This is the subtitle!",
        )
        for _ in range(100)
    ]
    yield from score_results(query, results)


plugin.run()
