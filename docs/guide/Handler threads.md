# Which thread runs your handlers

This page applies to V2 plugins (`"Language": "python_v2"` in `plugin.json`). On V1 every handler runs on the main thread, one process per request, as before.

## Plain handlers run on a worker thread

A V2 plugin is one long-lived process. Its event loop reads requests from Flow Launcher and writes the replies. Plain `def` handlers, including generators that `yield` results, run on a single worker thread so the loop keeps reading while they work.

There is only one worker, so two handlers never run at the same time. A request that arrives while another handler is busy waits for its turn.

## What happens when a query is cancelled

When the user keeps typing, Flow Launcher cancels the query that is still running. The plugin answers the cancelled request at once and drops whatever the handler later returns.

A plain handler cannot be stopped from outside, so a cancelled handler that has already started keeps running to the end. The next query starts after it finishes. A query that is cancelled while still waiting for its turn never starts.

If your query is slow and you want cancellation to stop the work itself, write the handler with `async def`. Async handlers run on the event loop and are cancelled at their next `await`:

```py
@plugin.on_method
async def query(query: str):
    data = await fetch(query)
    return [Result(title=item) for item in data]
```

Async handlers share the loop with the stdin reader, so keep blocking calls out of them.

## Keeping a handler on the main thread

Some objects only work on the thread that created them. A `sqlite3` connection opened when your plugin module is imported is the common case. Mark handlers that use such objects with `main_thread`:

```py
import sqlite3

from pyflowlauncher import Plugin, Result, main_thread

plugin = Plugin()
db = sqlite3.connect("bookmarks.db")


@plugin.on_method
@main_thread
def query(query: str):
    for (title,) in db.execute("SELECT title FROM bookmarks"):
        yield Result(title=title)
```

`main_thread` works above or below `@plugin.on_method`, and on methods of a class. A handler marked this way runs on the event loop, so while it runs the plugin cannot read a cancel request. Use it only when you need it.
