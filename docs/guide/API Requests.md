# Sending API requests to FLow Launcher

You can send special requests to Flow Launcher to control the launcher from your plugin. This communication is currently only one way.

!!! warning

    You can not send API requests from a query or context_menu method!

    Using API requests in this way will cause your plugin to fail!

## Sending a command from a Result

```py
--8<-- "docs/examples/guide/api_requests/example1.py"
```

The example above will change the query in Flow Launcher when the user selects your result.

## Sending a command from a Method

You can also send an API request in a custom method like so:

```py
--8<-- "docs/examples/guide/api_requests/example2.py"
```
