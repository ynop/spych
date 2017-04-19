import os
from spych.assets import ctm
from spych.assets import audacity

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

    TEXT_SEGMENTATION = 'text'
    RAW_TEXT_SEGMENTATION = 'raw_text'

    def __init__(self, segments=[], utterance_idx=None, key=TEXT_SEGMENTATION):
        self.segments = list(segments)
        self.utterance_idx = utterance_idx

        if key is None:
            self.key = Segmentation.TEXT_SEGMENTATION
        else:
            self.key = key

    @property
    def length(self):
        return len(self.segments)

    @property
    def first_segment(self):
        """ Return the first segment. """
        return self.segments[0]

    @property
    def last_segment(self):
        """ Return the last segment. """
        return self.segments[len(self.segments) - 1]

    def append(self, segment, start=-1, end=-1):
        if isinstance(segment, Segment):
            self.segments.append(segment)
        else:
            self.segments.append(Segment(segment, start, end))

    def to_text(self):
        """ Return segments concatenated as space separated string. """
        return ' '.join([segment.value for segment in self.segments])

    def to_audacity(self, path):
        """ Write the segmentation to a audacity label file. """
        audacity_segments = []

        for segment in self.segments:
            audacity_segments.append([segment.start, segment.end, segment.value])

        audacity.write_label_file(path, audacity_segments)

    def to_ctm(self, path):
        """ Write the segmentation to a ctm file. """
        ctm_segments = []

        for segment in self.segments:
            ctm_segments.append([self.utterance_idx, segment.start, segment.end - segment.start, segment.value])

        ctm.write_file(path, ctm_segments)

    @classmethod
    def from_text(cls, text, utterance_idx=None, key=TEXT_SEGMENTATION):
        """
        Create a segmentation from a string. It will be space separated into segments.

        :param text: The string to be segmented.
        :param utterance_idx: Utt id this segmentation belongs to.
        :param key: A key which identifies this segmentation.
        :return: Segmentation object
        """
        segments = [Segment(x.strip()) for x in list(filter(lambda x: x.strip() != '', text.strip().split(' ')))]

        return cls(segments, utterance_idx=utterance_idx, key=key)

    @classmethod
    def from_ctm(cls, path):
        """ Return a list of segmentations read from a ctm file. """

        ctm_content = ctm.read_file(path)

        segmentations = []

        for utt_id, info in ctm_content.items():
            segmentation = Segmentation(utterance_idx=utt_id)

            for segment_info in info:
                start = segment_info[1]
                duration = segment_info[2]
                label = segment_info[3]
                segment = Segment(label, start, start + duration)
                segmentation.segments.append(segment)

            segmentations.append(segmentation)

        return segmentations

    @classmethod
    def from_audacity(cls, path):
        """ Return the segmentation read from an audacity label file. """

        audacity_content = audacity.read_label_file(path)

        temp = os.path.splitext(path)[0]
        file_name = os.path.basename(temp)

        segmentation = Segmentation(utterance_idx=file_name)

        for currentItem in audacity_content:
            start = currentItem[0]
            end = currentItem[1]
            label = currentItem[2]
            segment = Segment(label, start, end)
            segmentation.segments.append(segment)

        return segmentation
