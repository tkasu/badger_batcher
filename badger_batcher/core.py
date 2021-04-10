"""Core functionality"""
from .utils import CacheIterator
from typing import Any, Iterable, Optional, List


class Batcher:
    """
    Utility that helps batching Iterables, main interface for badger_batcher.

    Example usage with max batch size, getting the results as list of lists:

    >>> records = (f"record: {rec}" for rec in range(21))
    >>> batcher = Batcher(records, max_batch_size=5)
    >>> batched_records = batcher.batches()
    >>> len(batched_records)
    5

    >>> records = [f"record: {rec}" for rec in range(5)]
    >>> batcher = Batcher(records, max_batch_size=2)
    >>> batcher.batches()
    [['record: 0', 'record: 1'], ['record: 2', 'record: 3'], ['record: 4']]

    Iterating the results one batch at a time:

    >>> records = (f"record: {rec}" for rec in range(21))
    >>> batcher = Batcher(records, max_batch_size=2)
    >>> for batch in batcher:
    ...       # do something
    ...       first_batch = batch
    ...       break
    >>> first_batch
    ['record: 0', 'record: 1']

    When processing big chunks of data, considering using iterator,
    as Batcher will not store the immidiate results of records:

    >>> import sys
    >>> records = (f"record: {rec}" for rec in range(sys.maxsize))
    >>> batcher = Batcher(records, max_batch_size=2)
    >>> for batch in batcher:
    ...       first_batch = batch
    ...       break
    >>> first_batch
    ['record: 0', 'record: 1']
    """

    records: Iterable[Any]
    max_batch_size: Optional[int]
    _iter_state: Optional[CacheIterator]

    def __init__(self, records, max_batch_size=None):
        self.records = records
        self.max_batch_size = max_batch_size
        self._iter_state = None

    def __iter__(self):
        self._iter_state = CacheIterator(item for item in self.records)
        return self

    def __next__(self):
        """
        Iterate Batcher's records iteration state with CacheIterator self._iter_state.
        CacheIterator is used to store previous value of the record iterator
        before batch splitting condition checks,
        as when split condition is met, the record should be moved to the next batch.
        This is achieved by retrieving the previous value from CacheIterator
        prev-property in the beginning of the loop.

        If split conditions are met, a batch is returned before self._iter_state
        is consumed.
        Otherwise, batch is returned when all records are consumed from CacheIterator.

        :return: List[Any] next batch
        :raises StopIteration: if self._iter_state is consumed.
        """
        if not self._iter_state:
            raise StopIteration

        batch = []
        if cache := self._iter_state.prev:
            batch.append(cache)

        if self._iter_state:
            for record in self._iter_state:
                if len(batch) >= self.max_batch_size:
                    return batch
                else:
                    batch.append(record)

        self._iter_state = None
        return batch

    def batches(self) -> List[List[Any]]:
        """
        Get all batches.

        Will load all batches to memory, when batching big sequences,
        considering iterating a Batcher instance instead.

        :return: batches of records in a list of lists
        """
        return list(iter(self))
