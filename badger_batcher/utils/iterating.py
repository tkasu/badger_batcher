from dataclasses import dataclass
from typing import Any, Iterable, Iterator, Optional


@dataclass
class CacheIterator:
    """
    Wrapper for iterables, that store the value fetch from an iterator
    to property prev during each iterator.

    This is sometimes useful with e.g. generators.

    >>> records = (1, 2, 3)
    >>> ci = CacheIterator(records)
    >>> it = iter(ci)
    >>> next(it)
    1
    >>> it.prev
    1
    """

    iterable: Iterable
    prev: Optional[Any] = None
    _iter_state: Optional[Iterator] = None

    def __iter__(self):
        self._iter_state = iter(self.iterable)
        return self

    def __next__(self):
        item = next(self._iter_state)
        self.prev = item
        return item
