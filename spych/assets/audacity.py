from spych.utils import textfile


def write_label_file(path, entries):
    """
    Writes an audacity label file.

    entries:

    [
        [start (seconds), end (seconds), label],
        [0.2, 2.2, 'hallo'],
        ...
    ]

    :param path: Path to write the file to.
    :param entries: List with entries to write.
    :return:
    """

    textfile.write_separated_lines(path, entries, separator=' ')


def read_label_file(path):
    """
    Reads the labels from an audacity label file.

    :param path: Path to the label file.
    :return: List of labels (start [sec], end [sec], label)
    """
    return textfile.read_separated_lines(path, separator='\t', max_columns=3)
