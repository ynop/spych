.. _section_usage:

Data Formats
============

Dataset
-------

A dataset is a folder consisting of the following files.

**wavs.txt**

The mapping between recording id to audio file path.

<recording-id> <wav-file-path>

Example:

.. code-block:: bash

    2014-03-17-09-45-16_Kinect-Beam train/2014-03-17-09-45-16_Kinect-Beam.wav
    2014-03-17-09-45-16_Realtek train/2014-03-17-09-45-16_Realtek.wav
    2014-03-17-09-45-16_Yamaha train/2014-03-17-09-45-16_Yamaha.wav
    2014-03-17-10-26-07_Realtek train/2014-03-17-10-26-07_Realtek.wav

**utterances.txt**

Defines the utterances within a recording. Every line defines one utterance.
If start and end are not given it's assumed the recording consist of a single utterance.
And end value of -1 indicates the end of the recording. Start and end are measured in seconds.

<utterance-id> <recording-id> <start> <end>


Example:

.. code-block:: bash

    1_hello 2014-03-17-09-45-16_Kinect-Beam
    1_hello_sam 2014-03-17-09-45-16_Realtek 0 -1
    2_this_is 2014-03-17-09-45-16_Yamaha 0 5
    3_goto 2014-03-17-09-45-16_Yamaha 5 -1

**transcriptions.txt (optional)**

List of transcriptions for utterances.

<utterance-id> <transcription>


Example:

.. code-block:: bash

    1_hello hi this is
    1_hello_sam hello sam
    2_this_is this is me
    3_goto go to the mall

**transcriptions_raw.txt (optional)**

List of raw transcriptions for utterances. These may contain punctuation, numbers that aren't written out, abbreviations ...

<utterance-id> <raw-transcription>

Example:

.. code-block:: bash

    1_hello hi, this is?
    1_hello_sam hello sam!!
    2_this_is this is me.
    3_goto go to the mall

**utt2spk.txt (optional)**

Defines the speakers of the utterances.

<utterance-id> <speaker-id>

Example:

.. code-block:: bash

    1_hello marc
    1_hello_sam marc
    2_this_is sam
    3_goto jenny

**speaker_info.json (optional)**

Contains any additional information about the speakers. Currently gender is the only defined key. Of course any other information can be stored.

Example:

.. code-block:: json

    {
        "marc": {"gender": "m"},
        "sam": {"gender": "m"},
        "jenny": {"gender": "f"}
    }