# Triggering Plugin methods

Flow Launcher can call custom methods created by your plugin as well. To do so simply register the method with your plugin.

You can register any Function by using the `on_method` decorator or by using the `add_method` method from `Plugin`.

## Example 1

```py
--8<-- "docs/examples/guide/plugin_methods/example1.py"
```

Alternativley you can register and add the Method to a Result in one line by using `action` method.

## Example 2

```py
--8<-- "docs/examples/guide/plugin_methods/example2.py"
```
