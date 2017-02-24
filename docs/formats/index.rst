Data Formats
============

Spych dataset
-------------

This describes, how a dataset with the spych format is saved on disk. Every dataset is a folder with a bunch of files.

**files.txt**

This file contains a list of every audio file in the dataset. Every file is identified by a unique id.
Every line in the file contains the mapping from file-id to the file-path for a single file. The filepath is the path to the audio file relative to the dataset folder.

.. code-block:: bash

    <recording-id> <wav-file-path>

Example:

.. code-block:: bash

    2014-03-17-09-45-16_Kinect-Beam train/2014-03-17-09-45-16_Kinect-Beam.wav
    2014-03-17-09-45-16_Realtek train/2014-03-17-09-45-16_Realtek.wav
    2014-03-17-09-45-16_Yamaha train/2014-03-17-09-45-16_Yamaha.wav
    2014-03-17-10-26-07_Realtek train/2014-03-17-10-26-07_Realtek.wav


**utterances.txt**

This file contains all utterances in the dataset. An utterance is a part of a file (A file can contain one or more utterances).
Every line in this file defines a single utterance, which consists of utterance-id, file-id, start and end. Start and end are measured in seconds within the file.
If end is -1 it is considered to be the end of the file (If the utterance is the full lenght of the file start and end are 0/-1).

.. code-block:: bash

    <utterance-id> <recording-id> <start> <end>

Example:

.. code-block:: bash

    1_hello 2014-03-17-09-45-16_Kinect-Beam
    1_hello_sam 2014-03-17-09-45-16_Realtek 0 -1
    2_this_is 2014-03-17-09-45-16_Yamaha 0 5
    3_goto 2014-03-17-09-45-16_Yamaha 5 -1

**speakers.json (optional)**

Contains any additional information about the speakers. Of course any other information can be stored.
For every speaker a key/value pairs can be defined. Basically any information can be saved, but there are some predefined values:

- gender : The gender of the speaker.
- synthesized : (True/False) If it is synthesized speech.
- synthesizer_voice : If it is synthesized, what voice was used.
- synthesizer_effects : If it is synthesized, what effect were applied.
- synthesizer_tool : If it is synthesized, what tool was used for synthesis.

Example:

.. code-block:: json

    {
        "marc": {
            "gender": "m",
            "synthesized": true,
            "synthesizer_tool": "MaryTTS"
        },
        "sam": {
            "gender": "m"
        },
        "jenny": {
            "gender": "m"
        }
    }

**utt2spk.txt**

This file contains the mapping from utterance to speaker, which gives the information which speaker has spoken a given utterance.
Every line contains one mapping from utterance-id to speaker-id.

.. code-block:: bash

    <utterance-id> <speaker-id>

Example:

.. code-block:: bash

    1_hello marc
    1_hello_sam marc
    2_this_is sam
    3_goto jenny

**segmentation_[x].txt**

There can be multiple segmentations in a dataset (e.g. text-transcription, raw-text-transcription - with punctuation).
Every segmentation is saved in a separate file with the prefix *segmentation_*.
A single file contains segmentations of a specific type of all utterances. A segmentation of an utterance can contain one or more tokens (e.g. in a text segmentation every word would be a token).
A token optionally can have a start and end time (in seconds within the utterance). For tokens without start/end defined -1 is set.
Every line in the file defines one token. The tokens are stored in order per utterance (e.g. 1. word, 2. word, 3. word, ...).

.. code-block:: bash

    <utterance-id> <start> <end> <token-value>

Example:

.. code-block:: bash

    1_hello -1 -1 hi
    1_hello -1 -1 this
    1_hello -1 -1 is
    1_hello_sam -1 -1 hello
    1_hello_sam -1 -1 sam
    2_this_is -1 -1 this
    2_this_is -1 -1 is
    2_this_is -1 -1 me
    3_goto -1 -1 go
    3_goto -1 -1 to
    3_goto -1 -1 the
    3_goto -1 -1 mall

**subview_[x].txt**

A subview defines a kind of a filter for dataset, which builds a subset. A dataset can contain multiple subviews.
Every subview can has multiple filter criteria:

- filtered-utterances : A list of utterance-ids which are used in the subview.
- filtered-speakers : A list of speaker-ids which are used in the subview.
- utterance_idx_patterns : A list of reg-expressions to match used utterances.
- speaker_idx_patterns : A list of reg-expressions to match used speakers.
- utterance_idx_not_patterns : A list of reg-expressions to match not used utterances.
- speaker_idx_not_patterns : A list of reg-expressions to match not used speakers.

The subview just contains the items, that match all criteria. Every line in the file contains one filter criterion.

.. code-block:: bash

    <criterion-name> <criterion-value>

Example:

.. code-block:: bash

    filtered_speaker_ids marc sam
    filtered_utt_ids 1_hello 2_this

Spych dataset legacy
--------------------

This is the old version of the spych dataset format. A dataset is a folder consisting of the following files.

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