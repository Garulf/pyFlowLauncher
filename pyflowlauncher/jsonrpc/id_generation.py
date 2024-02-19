import itertools
from typing import Iterator


def incremental_int(start: int = 1) -> Iterator[int]:
    return itertools.count(start)
