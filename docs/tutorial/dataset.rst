Dataset Tutorial
================

Load / Save a dataset
---------------------

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


Generate batches
----------------

For training deep neural networks the data needs to be split up in batches. For this purpose the :py:class:`spych.dataset.iteration.BatchGenerator` was implemented.
It basically generates batches of a specified size with randomly selected utterances. One special thing is that you can specify multiple datasets.
If you do so it always first checks for common utterance ids over all given datasets and just uses these to create the batches.
It can be used to in different ways.

One way is to generate batches that contain a list of utterances.

.. code-block:: python

    # create the batch generator
    batcher = iteration.BatchGenerator(dataset_a)

    # get generator over batches with the desired batch size (number of utterances per batch)
    gen = batcher.generate_utterance_batches(512)

    # now you can iterate over the batches
    for batch in gen:

        # batch is now a list of utterance-ids
        print(batch)

Another way is to generate batches that contains the concatenated features of given number of utterances.

.. code-block:: python

    # create the batch generator
    batcher = iteration.BatchGenerator([dataset_a, dataset_b])

    # get generator over batches with the desired batch size (number of utterances per batch)
    gen = batcher.generate_feature_batches('mfcc', 512, splice_size=0, splice_step=1, repeat_border_frames=True)

    # now you can iterate over the batches
    for batch in gen:

        # batch is now a list of features as np-arrays [from dataset_a, from dataset_b]
        print(len(batch)) # --> 2

