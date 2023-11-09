

class EventHandler:

    def __init__(self):
        self._methods = {}

    def add_method(self, method, *, name=None):
        self._methods[name or method.__name__] = method

    def add_methods(self, methods):
        for method in methods:
            self.add_method(method)

    def __call__(self, method, *args, **kwargs):
        return self._methods[method](*args, **kwargs)
