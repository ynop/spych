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

    @classmethod
    def from_tuples(cls, tuples):
        items = []

        for value in tuples:
            items.append(SequenceItem(value[0], value[1], value[2]))

        return cls(items)