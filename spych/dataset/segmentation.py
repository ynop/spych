TEXT_SEGMENTATION = 'text'
RAW_TEXT_SEGMENTATION = 'raw_text'


class Segment(object):
    __slots__ = ['value', 'start', 'end']

    def __init__(self, value, start=-1, end=-1):
        self.value = value
        self.start = start
        self.end = end


class Segmentation(object):
    __slots__ = ['segments', 'utterance_idx', 'key']

    def __init__(self, segments=[], utterance_idx=None, key=TEXT_SEGMENTATION):
        self.segments = list(segments)
        self.utterance_idx = utterance_idx

        if key is None:
            self.key = TEXT_SEGMENTATION
        else:
            self.key = key

    def to_text(self):
        return ' '.join([segment.value for segment in self.segments])

    @classmethod
    def from_text(cls, text, utterance_idx=None, key=TEXT_SEGMENTATION):
        """
        Create a segmentation from a string. It will be space separated into segments.

        :param text: The string to be segmented.
        :param utterance_idx: Utt id this segmentation belongs to.
        :param key: A key which identifies this segmentation.
        :return: Segmentation object
        """
        segments = [Segment(x) for x in text.strip().split(' ')]

        return cls(segments, utterance_idx=utterance_idx, key=key)
