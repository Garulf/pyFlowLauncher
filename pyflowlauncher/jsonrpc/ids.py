from itertools import count


class ID:

    def __init__(self, start=1, step=1):
        self._counter = count(start, step)
        self._current = start

    def __next__(self):
        self._current = next(self._counter)
        return self._current

    def __iter__(self):
        return self

    @property
    def current(self):
        return self._current
