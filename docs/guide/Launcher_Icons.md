# Using icons included with Flow Launcher

Flow Launcher comes with a decent amount of icons that it uses throughout it's UI and plugins.

You can use some of these icons in your plugin by importing from the `icons` module.

!!! warning

    If PyFlowLauncher is unable to locate the Flow Launcher directory these icons may not be loaded!

    This will not crash your plugin but will leave the icon blank.

## Example

```py
from pyflowlauncher import Plugin, Result, send_results
from pyflowlauncher.result import ResultResponse
from pyflowlauncher.icons import ICONS

plugin = Plugin()


@plugin.on_method
def query(query: str) -> ResultResponse:
    r = Result(
        Title="This is a title!",
        SubTitle="This is the subtitle!",
        IcoPath=ICONS["app"]
    )
    return send_results([r])


plugin.run()
```
