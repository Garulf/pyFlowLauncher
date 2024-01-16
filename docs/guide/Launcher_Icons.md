# Using icons included with Flow Launcher

Flow Launcher comes with a decent amount of icons that it uses throughout it's UI and plugins.

You can use some of these icons in your plugin by importing from the `icons` module.

!!! warning

    If PyFlowLauncher is unable to locate the Flow Launcher directory these icons may not be loaded!

    This will not crash your plugin but will leave the icon blank.

## Example

```py
--8<-- "docs/examples/guide/launcher_icons/example1.py"
```
