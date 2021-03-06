import collections

from spych.utils import textfile


def write_file(path, entries):
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

    textfile.write_separated_lines(path, entries, separator=" ")


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
