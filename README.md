[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/garulf/pyflowlauncher/tests.yaml?style=flat-square)](https://github.com/Garulf/pyFlowLauncher/actions/workflows/tests.yaml) [![buymeacoffee](https://img.shields.io/badge/buy%20me%20a%20coffee-yellow.svg?style=flat-square&logo=buymeacoffee&logoColor=000)](https://www.buymeacoffee.com/garulf)

# PyFlowLauncher

PyFlowLauncher is an API that allows you to quickly create plugins for Flow Launcher!

## Installation

Install via pip:

```py
python -m pip install pyflowlauncher
```

## Usage

### Basic plugin

A basic plugin using a function as the query method.

```py
from pyflowlauncher import Plugin, Result, send_results
from pyflowlauncher.result import ResultResponse

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

### Advanced plugin

A more advanced usage using a `Method` class as the query method.

```py
from pyflowlauncher import Plugin, Result, Method
from pyflowlauncher.result import ResultResponse

plugin = Plugin()


class Query(Method):

    def __call__(self, query: str) -> ResultResponse:
        r = Result(
            Title="This is a title!",
            SubTitle="This is the subtitle!"
        )
        self.add_result(r)
        return self.return_results()

plugin.add_method(Query())
plugin.run()
```
