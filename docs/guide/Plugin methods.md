# Triggering Plugin methods

Flow Launcher can call custom methods created by your plugin as well. To do so simply register the method with your plugin.

You can register any function by using the `on_method` decorator or by using the `add_method` method from `Plugin`.

## Returning results

Methods decorated with `@plugin.on_method` support several return styles — the framework normalizes all of them automatically:

```py
# yield a single result
@plugin.on_method
def query(query: str):
    yield Result(title="Hello!")

# yield multiple results
@plugin.on_method
def query(query: str):
    for item in data:
        yield Result(title=item)

# return a list of results
@plugin.on_method
def query(query: str):
    return [Result(title="a"), Result(title="b")]

# return a single result
@plugin.on_method
def query(query: str):
    return Result(title="Hello!")
```

## Example 1

```py
--8<-- "docs/examples/guide/plugin_methods/example1.py"
```

Alternatively you can register and add the Method to a Result in one line by using the `action` method.

## Example 2

```py
--8<-- "docs/examples/guide/plugin_methods/example2.py"
```
