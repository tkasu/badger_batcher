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


Split records based max limit for batch size:

.. code-block:: python

    >>> records = [f"record: {rec}" for rec in range(5)]
    >>> batcher = Batcher(records, max_batch_size=2)
    >>> batcher.batches()
    [['record: 0', 'record: 1'], ['record: 2', 'record: 3'], ['record: 4']]

Split records with max limit for batch size and max limit for record size:

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

When processing big chunks of data, consider iterating instead:

.. code-block:: python

    >>> import sys

    >>> records = (f"record: {rec}" for rec in range(sys.maxsize))
    >>> batcher = Batcher(records, max_batch_size=2)
    >>> for batch in batcher:
    ...       # do something for each batch
    ...       some_fancy_fn(batch)

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
