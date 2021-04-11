#!/usr/bin/env python

"""Tests for `badger_batcher` package."""

import pytest  # noqa: F401
from badger_batcher import Batcher


def test_badger_max_batch_size_only():
    records = (f"record: {rec}" for rec in range(21))

    batcher = Batcher(records, max_batch_size=5)
    batched_records = batcher.batches()
    assert len(batched_records) == 5
    assert batched_records[1][0] == "record: 5"


def test_empty_records():
    records = []
    batcher = Batcher(records, max_batch_size=5)
    batched_records = batcher.batches()
    assert batched_records == [[]]


def test_no_filters():
    records = [f"record: {rec}" for rec in range(21)]
    batcher = Batcher(records)
    batched_records = batcher.batches()
    assert batched_records == [records]

