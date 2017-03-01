TEXT_SEGMENTATION = 'text'
RAW_TEXT_SEGMENTATION = 'raw_text'

from spych.assets import ctm
from spych.assets import audacity

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
        segments = [Segment(x.strip()) for x in list(filter(lambda x: x.strip() != '', text.strip().split(' ')))]

        return cls(segments, utterance_idx=utterance_idx, key=key)

    @classmethod
    def from_ctm(cls,path):
        """ Return a list of segmentations from a ctm file"""
        ctm_content = ctm.read_file(path)
        segmentations = []
        for utt_id,info in ctm_content.items():
            segmentation = Segmentation(utterance_idx=utt_id)
            for segment_info in info:
                start = segment_info[1]
                duration = segment_info[2]
                label = segment_info[3]
                segment = Segment(label,start,start+duration)
                segmentation.segments.append(segment)
            segmentations.append(segmentation)
        return segmentations

    def to_audacity(self, path):
        """ Return a list of segmentations from a ctm file"""

        ctm_content = ctm.read_file(path)
        audacity_segments = []

        for segment in self.segments:
            audacity_segments.append([segment.start,segment.end,segment.value])

        audacity.write_label_file(path,audacity_segments)
