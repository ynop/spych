Dataset Tutorial
================

Load / Save
-----------

To load a dataset in python from a directory, the :py:func:`spych.data.dataset.Dataset.load` can be used.
By default spych expects the dataset in the spych format. If the dataset has another format, the loader argument has to be provided.

.. code-block:: python

    # create a loader
    kaldi_loader = loader.KaldiDatasetLoader()

    # load the dataset
    ds = dataset.Dataset.load('/path/to/the/dataset/folder', loader=kaldi_loader)

For saving a dataset the same principle is used. You can either use :py:func:`spych.data.dataset.Dataset.save_at` or  :py:func:`spych.data.dataset.Dataset.save`.
When using the latter the dataset object needs to have a path defined, where to save it. Every dataset is associated with a loader (by default the spych loader),
which it will use for saving, if not defined otherwise (as in the following example).

.. code-block:: python

    # create a loader
    kaldi_loader = loader.KaldiDatasetLoader()

    # save the dataset
    ds.save_at('/path/to/the/dataset/folder', loader=kaldi_loader)

The load and save functions also can be used to copy or convert a dataset. Following an example that loads a dataset from the spych format and stores it as kaldi format in another place.

.. code-block:: python

    # load it (spych is default, so no loader has to be defined)
    ds = dataset.Dataset.load('/path/to/the/spych/dataset/folder')

    # save it in kaldi format (loader can also be passed with its name)
    ds.save_at('/path/to/save/as/kaldi/format', loader='kaldi')

Now by default the audio files and feature files are not copied to the new path. There will be just a relative path to the old folder. If you also want to copy the files:

.. code-block:: python

    ds.save_at('/path/to/save/as/kaldi/format', loader='kaldi', copy_files=True)


Generate batches
----------------

For training deep neural networks the data needs to be split up in batches. For this purpose the :py:class:`spych.data.dataset.BatchGenerator` was implemented.
It basically generates batches of a specified size with randomly selected utterances. One special thing is that you can specify multiple datasets.
If you do so it always first checks for common utterance ids over all given datasets and just uses these to create the batches.
It can be used to in different ways.

One way is to generate batches that contain a list of utterances.

.. code-block:: python

    # create the batch generator
    batcher = dataset.BatchGenerator(dataset_a)

    # get generator over batches with the desired batch size (number of utterances per batch)
    gen = batcher.generate_utterance_batches(512)

    # now you can iterate over the batches
    for batch in gen:

        # batch is now a list of utterance-ids
        print(len(batch)) # --> 512 (not the last batch)

Another way is to generate batches that contains the concatenated features of given number of utterances.

.. code-block:: python

    # create the batch generator
    batcher = dataset.BatchGenerator([dataset_a, dataset_b])

    # get generator over batches with the desired batch size (number of utterances per batch)
    gen = batcher.generate_feature_batches('mfcc', 512, splice_size=0, splice_step=1, repeat_border_frames=True)

    # now you can iterate over the batches
    for batch in gen:

        # batch is now a list of features as np-arrays [from dataset_a, from dataset_b]
        print(len(batch)) # --> 2

