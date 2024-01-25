from pyflowlauncher import Plugin, Result, send_results
from pyflowlauncher.result import ResultResponse
from pyflowlauncher.utils import score_results

plugin = Plugin()


@plugin.on_method
def query(query: str) -> ResultResponse:
    results = []
    for _ in range(100):
        r = Result(
            Title="This is a title!",
            SubTitle="This is the subtitle!",
        )
        results.append(r)
    return send_results(score_results(query, results))


plugin.run()
