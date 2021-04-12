#!/usr/bin/env python

"""Tests for `badger_batcher` package."""

import pytest  # noqa: F401
from badger_batcher import Batcher
from badger_batcher.errors import RecordSizeExceeded


def test_badger_max_batch_len_only():
    records = (f"record: {rec}" for rec in range(21))

    batcher = Batcher(records, max_batch_len=5)
    batched_records = batcher.batches()
    assert len(batched_records) == 5
    assert batched_records[1][0] == "record: 5"


def test_empty_records():
    records = []
    batcher = Batcher(records, max_batch_len=5)
    batched_records = batcher.batches()
    assert batched_records == [[]]


def test_no_filters():
    records = [f"record: {rec}" for rec in range(21)]
    batcher = Batcher(records)
    batched_records = batcher.batches()
    assert batched_records == [records]


def test_only_max_record_size_no_exceed():
    records = [b"aaaa", b"bb", b"ccccc", b"d"]
    batcher = Batcher(records, max_record_size=5, size_calc_fn=len)
    batched_records = batcher.batches()
    assert batched_records == [records]


def test_only_max_record_size_exception():
    records = [b"aaaa", b"bb", b"ccccc", b"d"]
    batcher = Batcher(records, max_record_size=4, size_calc_fn=len)
    with pytest.raises(RecordSizeExceeded):
        _ = batcher.batches()


def test_only_max_record_size_skip():
    records = [b"aaaa", b"bb", b"ccccc", b"d"]
    batcher = Batcher(
        records, max_record_size=4, size_calc_fn=len, when_record_size_exceeded="skip"
    )
    batched_records = batcher.batches()
    assert batched_records == [[b"aaaa", b"bb", b"d"]]


def test_max_record_size_custom_fn():
    records = ["aaaa", "bb", "ccccc", "d"]
    batcher = Batcher(
        records,
        max_batch_len=2,
        max_record_size=9,
        size_calc_fn=lambda r: 10 if "b" in r else 0,
        when_record_size_exceeded="skip",
    )
    batched_records = batcher.batches()
    assert batched_records == [["aaaa", "ccccc"], ["d"]]


def test_max_output_size_and_batch_len():
    records = [b"aaaa", b"bb", b"ccccc", b"d"]
    batcher = Batcher(
        records,
        max_batch_len=2,
        max_record_size=4,
        size_calc_fn=len,
        when_record_size_exceeded="skip",
    )
    batched_records = batcher.batches()
    assert batched_records == [[b"aaaa", b"bb"], [b"d"]]


def test_missing_size_calc_fn():
    records = [b"aaaa", b"bb", b"ccccc", b"d"]
    with pytest.raises(ValueError):
        _ = Batcher(records, max_record_size=4)


def test_invalid_when_record_size_exceeded_fn():
    records = [b"aaaa", b"bb", b"ccccc", b"d"]
    with pytest.raises(ValueError):
        _ = Batcher(
            records,
            max_record_size=4,
            size_calc_fn=len,
            when_record_size_exceeded="party",
        )


def test_only_max_batch_size_skip():
    records = [b"aaaa", b"b", b"ccc", b"toolargeforbatch", b"dd", b"e"]
    batcher = Batcher(
        records, max_batch_size=5, size_calc_fn=len, when_record_size_exceeded="skip"
    )
    batched_records = batcher.batches()
    assert batched_records == [[b"aaaa", b"b"], [b"ccc", b"dd"], [b"e"]]


def test_max_batch_size_and_max_batch_len_skip():
    records = [b"a", b"a", b"a", b"b", b"ccc", b"toolargeforbatch", b"dd", b"e"]
    batcher = Batcher(
        records,
        max_batch_len=3,
        max_batch_size=5,
        size_calc_fn=len,
        when_record_size_exceeded="skip",
    )
    batched_records = batcher.batches()
    assert batched_records == [
        [b"a", b"a", b"a"],
        [b"b", b"ccc"],
        [b"dd", b"e"],
    ]


def test_max_batch_size_and_max_batch_len_max_record_size_skip():
    records = [b"a", b"a", b"a", b"b", b"ccc", b"bbbb", b"dd", b"e"]
    batcher = Batcher(
        records,
        max_batch_len=3,
        max_record_size=3,
        max_batch_size=5,
        size_calc_fn=len,
        when_record_size_exceeded="skip",
    )
    batched_records = batcher.batches()
    assert batched_records == [
        [b"a", b"a", b"a"],
        [b"b", b"ccc"],
        [b"dd", b"e"],
    ]


def test_max_batch_size_missing_size_calc_fn():
    records = [b"aaaa", b"bb", b"ccccc", b"d"]
    with pytest.raises(ValueError):
        _ = Batcher(records, max_batch_size=4)


def test_max_batch_size_invalid_when_record_size_exceeded_fn():
    records = [b"aaaa", b"bb", b"ccccc", b"d"]
    with pytest.raises(ValueError):
        _ = Batcher(
            records,
            max_batch_size=4,
            size_calc_fn=len,
            when_record_size_exceeded="party",
        )


def test_max_encode_before_batching():
    records = ["a", "a", "a", "b", "ccc", "bbbb", "dd", "e"]
    encoded_records_gen = (record.encode("utf-16-le") for record in records)

    batcher = Batcher(
        encoded_records_gen,
        max_batch_len=3,
        max_record_size=6,
        max_batch_size=10,
        size_calc_fn=len,
        when_record_size_exceeded="skip",
    )
    batched_records = batcher.batches()
    assert batched_records == [
        [b"a\x00", b"a\x00", b"a\x00"],
        [b"b\x00", b"c\x00c\x00c\x00"],
        [b"d\x00d\x00", b"e\x00"],
    ]
