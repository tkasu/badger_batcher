"""Core functionality"""
from .errors import RecordSizeExceeded
from .utils import CacheIterator
from typing import Any, Callable, Iterable, Optional, List


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

    >>> records = [b"aaaa", b"bb", b"ccccc", b"d"]
    >>> batcher = Batcher(
    ... records,
    ... max_batch_size=2,
    ... max_record_size=4,
    ... size_calc_fn=len,
    ... when_record_size_exceeded="skip",
    ... )
    >>> batcher.batches()
    [[b'aaaa', b'bb'], [b'd']]

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
    max_record_size = Optional[int]
    size_calc_fn = Optional[Callable[[Any], int]]
    when_record_size_exceeded = Optional[str]
    _iter_state: Optional[CacheIterator]

    def __init__(
        self,
        records,
        max_batch_size=None,
        max_record_size=None,
        size_calc_fn=None,
        when_record_size_exceeded="raises",
    ):
        """
        :param records: Iterable of records to batch
        :param max_batch_size: Optional max batch size
        :param max_record_size: Optional max record size,
            if used size_calc_fn must be defined
        :param size_calc_fn: function from record type T -> int used to calculated size
        :param when_record_size_exceeded: What to do when when size limit is exceeded
        :raises ValueError: in case of incompatible parameters
        """
        self.records = records
        self.max_batch_size = max_batch_size

        if max_record_size and not size_calc_fn:
            raise ValueError("max_record_size requires size_calc_fn to be specified")
        self.max_record_size = max_record_size
        self.size_calc_fn = size_calc_fn

        exceed_acceptable_values = ["raises", "skip"]
        if when_record_size_exceeded not in exceed_acceptable_values:
            raise ValueError(
                f"when_record_size_exceeded should be in: {exceed_acceptable_values}"
            )
        self.when_record_size_exceeded = when_record_size_exceeded

        self._iter_state = None

    def _check_max_batch_size(self, batch) -> bool:
        if self.max_batch_size:
            return len(batch) >= self.max_batch_size
        else:
            return False

    def _check_max_record_size(self, record) -> bool:
        if self.max_record_size:
            # mypy ignore: https://github.com/python/mypy/issues/708
            return self.size_calc_fn(record) > self.max_record_size  # type: ignore
        else:
            return False

    def __iter__(self):
        """
        Makes Batcher iterable

        Passes a generator to CacheIteration, as __next__ is starting iteration of
        _iter_state multiple times, but we don't want it to start all over again.
        """
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
        :raises NotImplementedError: in case of non-valid value
            for self.when_record_size_exceeded
        :raises RecordSizeExceeded if self.when_record_size_exceeded is `raises`
            and threshold is exceeded
        """
        if not self._iter_state:
            raise StopIteration

        batch = []
        if cache := self._iter_state.prev:
            batch.append(cache)

        if self._iter_state:
            for record in self._iter_state:

                if self._check_max_record_size(record):
                    if self.when_record_size_exceeded == "raises":
                        raise RecordSizeExceeded(
                            f"The following record exceeded the size limit: {record}"
                        )
                    elif self.when_record_size_exceeded == "skip":
                        continue
                    else:
                        raise NotImplementedError(
                            f"Value `{self.when_record_size_exceeded}` not supported "
                            f"for when_record_size_exceeded"
                        )

                if self._check_max_batch_size(batch):
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
