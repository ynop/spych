Dataset Tutorial
================

Load/Save a dataset
-------------------

To load a dataset in python from a directory, the :py:func:`spych.dataset.dataset.Dataset.load` can be used.
By default spych expects the dataset in the spych format. If the dataset has another format, the loader argument has to be provided.

.. code-block:: python

    # create a loader
    kaldi_loader = kaldi.KaldiDatasetLoader()

    # load the dataset
    ds = dataset.Dataset.load('/path/to/the/dataset/folder', loader=kaldi_loader)

For saving a dataset the same principle is used. You can either use :py:func:`spych.dataset.dataset.Dataset.save_at` or  :py:func:`spych.dataset.dataset.Dataset.save`.
When using the latter the dataset object needs to have a path defined, where to save it. Every dataset has is associated with a loader (by default the spych loader),
which it will use for saving, if not defined otherwise (as in the following example).

.. code-block:: python

    # create a loader
    kaldi_loader = kaldi.KaldiDatasetLoader()

    # save the dataset
    ds.save_at('/path/to/the/dataset/folder', loader=kaldi_loader)
