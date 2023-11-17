## Sending API requests to FLow Launcher

You can send special requests to Flow Launcher to control the launcher from your plugin. This communication is currently only one way.

!!! warning

    You can not send API requests from a query or context_menu method! 
    
    Using API requests in this way will cause your plugin to fail!

### Sending a command from a Result

```
from pyflowlauncher import Plugin, Result, send_results, api
from pyflowlauncher.result import JsonRPCAction, ResultResponse

plugin = Plugin()


@plugin.on_method
def query(query: str) -> ResultResponse:
    r = Result(
        Title="This is a title!",
        SubTitle="This is the subtitle!",
        IcoPath="icon.png",
        JsonRPCAction=api.change_query("This is a new query!"),
    )
    return send_results([r])


plugin.run()
```

The example above will change the query in Flow Launcher when the user selects your result.


### Sending a command from a Method

You can also send an API request in a custom method like so:

```
from pyflowlauncher import Plugin, Result, send_results, api
from pyflowlauncher.result import JsonRPCAction, ResultResponse

plugin = Plugin()


@plugin._on_method
def example_method():
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
```