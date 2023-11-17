## Installation

Install via pip:
```
python -m pip install pyflowlauncher
```

## Usage

#### Basic plugin
```
from pyflowlauncher import Plugin, Result, send_results
from pyflowlauncher.result import, ResultResponse

plugin = Plugin()


@plugin.on_method
def query(query: str) -> ResultResponse:
    r = Result(
        Title="This is a title!",
        SubTitle="This is the subtitle!",
        IcoPath="icon.png"
    )
    return send_results([r])


plugin.run()
```
