import os
import collections

from spych.utils import textfile
from spych.assets import audacity

def write_file(path,entries):
    """
       Writes a ctm file.

       entries:

       [
           [waveform_name, waveform_channel, start (seconds), duration (seconds), label],
           [2015-02-09-15-08-07_Kinect-Beam, 1, 0.82, 0.57, "Jacques"],

           ...
       ]

       :param path: Path to write the file to.
       :param entries: List with entries to write.
       :return:
       """

    textfile.write_separated_lines(path, entries, separator="\t")


def read_file(path):
    """
    Reads a ctm file.

    Returns dict:

    {
        'utt-wav-id': [
            [channel, start (seconds), duration (seconds), label, confidence],
            ['1', 0.00, 0.07, 'HI', 1],
            ['1', 0.09, 0.08, 'AH', 1],
            ...
        ],
        ...
    }

    :param path: Path to the file
    :return: Dictionary with entries.
    """
    gen = textfile.read_separated_lines_generator(path, max_columns=6, ignore_lines_starting_with=[';;'])

    utterances = collections.defaultdict(list)

    for record in gen:
        values = record[1:len(record)]

        for i in range(len(values)):
            if i == 1 or i == 2 or i == 4:
                values[i] = float(values[i])

        utterances[record[0]].append(values)

    return utterances


def to_audacity_label_file(path, target_folder):
    records = read_file(path)

    for wav_name, labels in records.items():
        label_basename = os.path.splitext(os.path.basename(wav_name))[0]
        label_file = os.path.join(target_folder, '{}.txt'.format(label_basename))

        label_entries = []

        for ctm_entries in labels:
            label_entries.append([ctm_entries[1], ctm_entries[1] + ctm_entries[2], ctm_entries[3]])

        audacity.write_label_file(label_file, label_entries)
