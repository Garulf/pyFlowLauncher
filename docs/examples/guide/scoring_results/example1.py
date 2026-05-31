from pyflowlauncher import Plugin, Result, send_results
from pyflowlauncher.models.json_rpc import JsonRPCResponse
from pyflowlauncher.utils import score_results

plugin = Plugin()


@plugin.on_method
def query(query: str) -> JsonRPCResponse:
    results = []
    for _ in range(100):
        r = Result(
            title="This is a title!",
            subtitle="This is the subtitle!",
        )
        results.append(r)
    return send_results(score_results(query, results))


plugin.run()
