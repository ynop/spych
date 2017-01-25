from spych.assets import ctm
from spych.assets import audacity


class SequenceItem(object):
    """
    Represents an item in a sequence. An item at least consists of a label. It may has start time and duration in seconds.
    """

    def __init__(self, label, start=-1.0, duration=-1.0):
        """
        Create instance.

        :param label: Label
        :param start: Start time [seconds]
        :param duration: Duration [seconds]
        """
        self.label = label
        self.start = start
        self.duration = duration


class Sequence(object):
    """
    Represents a sequence of items.
    """

    def __init__(self, items=[]):
        self.items = list(items)

    def items_in_interval(self, start, end):
        """
        Return all items and their indices that intersect the given range.

        :param start: start of interval in seconds
        :param end: end of interval in seconds
        :return: list of (index, item) tuples
        """

        if end <= start:
            raise ValueError("End ({}) of range has to greater than start ({}).".format(end, start))

        matching_items = []

        for index, item in enumerate(self.items):
            if not (end <= item.start or start >= item.start + item.duration):
                matching_items.append((index, item))

        return matching_items

    def append_item(self, item):
        self.items.append(item)

    @classmethod
    def from_tuples(cls, tuples):
        """
        Return sequence from list of tuples (label, start, duration).
        """
        items = []

        for value in tuples:
            items.append(SequenceItem(value[0], value[1], value[2]))

        return cls(items)

    @classmethod
    def from_ctm(cls, path):
        """
        Return list of sequences from ctm file.
        """
        ctm_entries = ctm.read_file(path)
        sequences = {}

        for wav_name, segments in ctm_entries.items():
            sequence = cls()

            for segment in segments:
                item = SequenceItem(segment[3], start=segment[1], duration=segment[2])
                sequence.append_item(item)

            sequences[wav_name] = sequence

        return sequences

    @classmethod
    def from_audacity_labels(cls, path):
        """
        Return sequence from audacity label file.
        """
        sequence = cls()
        audacity_entries = audacity.read_label_file(path)

        for segment in audacity_entries:
            item = SequenceItem(segment[2], start=segment[0], duration=segment[1] - segment[0])
            sequence.append_item(item)

        return sequence
