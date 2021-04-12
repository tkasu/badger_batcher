==============
Badger Batcher
==============


.. image:: https://img.shields.io/pypi/v/badger_batcher.svg
        :target: https://pypi.python.org/pypi/badger_batcher

.. image:: https://travis-ci.com/tkasu/badger_batcher.svg?branch=master
        :target: https://travis-ci.com/tkasu/badger_batcher

.. image:: https://readthedocs.org/projects/badger-batcher/badge/?version=latest
        :target: https://badger-batcher.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




Badger Batcher contains useful utilities for batching a sequence on records


* Free software: MIT license
* Documentation: https://badger-batcher.readthedocs.io.


Installation
------------

.. code-block:: bash

    $ pip install badger_batcher


Features
--------

Import Batcher:

.. code-block:: python

    >>> from badger_batcher import Batcher


Split records based max limit for batch len:

.. code-block:: python

    >>> records = [f"record: {rec}" for rec in range(5)]
    >>> batcher = Batcher(records, max_batch_size=2)
    >>> batcher.batches()
    [['record: 0', 'record: 1'], ['record: 2', 'record: 3'], ['record: 4']]

Split records with max limit for batch len and max limit for record size:

.. code-block:: python

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

Split records with max batch len and size:

.. code-block:: python

    >>> records = [b"a", b"a", b"a", b"b", b"ccc", b"toolargeforbatch", b"dd", b"e"]
    >>> batcher = Batcher(
    ... records,
    ... max_batch_len=3,
    ... max_batch_size=5,
    ... size_calc_fn=len,
    ... when_record_size_exceeded="skip",
    ... )
    >>> batcher.batches()
    [[b'a', b'a', b'a'], [b'b', b'ccc'], [b'dd', b'e']]

When processing big chunks of data, consider iterating instead:

.. code-block:: python

    >>> import sys

    >>> records = (f"record: {rec}" for rec in range(sys.maxsize))
    >>> batcher = Batcher(records, max_batch_size=2)
    >>> for batch in batcher:
    ...       # do something for each batch
    ...       some_fancy_fn(batch)

If you need to encode records before applying the batcher, just encode it before applying.
Batcher will not eagerly realize the whole iterable, so use a generator for bigger iterables.

.. code-block:: python

    >>> records = ["a", "a", "a", "b", "ccc", "bbbb", "dd", "e"]
    >>> encoded_records_gen = (record.encode("utf-16-le") for record in records)

    >>> batcher = Batcher(
    ... encoded_records_gen,
    ... max_batch_len=3,
    ... max_record_size=6,
    ... max_batch_size=10,
    ... size_calc_fn=len,
    ... when_record_size_exceeded="skip",
    ... )

    >>> batched_records = batcher.batches()
    [
        [b"a\x00", b"a\x00", b"a\x00"],
        [b"b\x00", b"c\x00c\x00c\x00"],
        [b"d\x00d\x00", b"e\x00"],
    ]

Full example for e.g. Kinesis Streams like processing

.. code-block:: python

    import random
    from badger_batcher import Batcher


    def get_records():
        records = (
            f"""{{'id': '{i}', 'body': {('x' * random.randint(100_000, 7_000_000))}}}"""
            for i in range(10_000)
        )
        return records


    records = get_records()
    encoded_records = (record.encode("utf-8") for record in records)

    batcher = Batcher(
        encoded_records,
        max_batch_len=500,
        max_record_size=1000 * 1000,
        max_batch_size=5 * 1000 * 1000,
        size_calc_fn=len,
        when_record_size_exceeded="skip",
    )

    for i, batch in enumerate(batcher):
        # do something


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
