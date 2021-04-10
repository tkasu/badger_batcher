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


Features
--------

Split records based max limit for batch size:

.. code-block:: python

    >>> records = [f"record: {rec}" for rec in range(5)]
    >>> batcher = Batcher(records, max_batch_size=2)
    >>> batcher.batches()
    [['record: 0', 'record: 1'], ['record: 2', 'record: 3'], ['record: 4']]

When processing big chunks of data, consider iterating instead:

.. code-block:: python

    >>> import sys
    >>> records = (f"record: {rec}" for rec in range(sys.maxsize))
    >>> batcher = Batcher(records, max_batch_size=2)
    >>> for batch in batcher:
    ...       first_batch = batch
    ...       break
    >>> first_batch
    ['record: 0', 'record: 1']

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
