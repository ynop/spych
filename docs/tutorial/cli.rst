Command Line Tutorial
=====================

Dataset
-------

For the following examples it is assumed we are in a directory containing a dataset in the spych format::

    $ ls
    audio_files
    features_fbank
    features_mfcc
    features_mfcc_cmn_deltas
    features_mfcc_cmvn_deltas
    features_spectrum
    features.txt
    files.txt
    segmentation_raw_text.txt
    segmentation_text.txt
    speakers.json
    utt2spk.txt
    utterances.txt

Display info
^^^^^^^^^^^^

Display information for a dataset (num. speakers, num. utterances, ... )::

    spych dataset info .

Output::

    Dataset .:

    Path                        /some/path/data/audio/real_test
    Num. Utterances             1080
    Num. Files                  1080
    Num. Speakers               16

    Segmentations:              raw_text, text
    Features:                   mfcc, spectrum, mfcc_cmvn_deltas, fbank, mfcc_cmn_deltas
    Subviews:

For detailed info (feature statistics) append the **--detailed** flag.