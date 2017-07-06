import enum

import numpy as np

from . import base
from spych.utils import array


class SpliceStage(base.ProcessingStage):
    def __init__(self, splice_size=4, splice_step=1):
        self.splice_size = splice_size
        self.splice_step = splice_step

    def process(self, feature_matrix):
        processed = array.splice_features(feature_matrix, self.splice_size, self.splice_step, repeat_border_frames=True)

        return processed.copy()


class UnspliceMergeType(enum.Enum):
    COMPUTE_MEAN = 'mean'
    TAKE_CENTER_FRAME = 'center_frame'


class UnspliceStage(base.ProcessingStage):
    def __init__(self, splice_size=4, splice_step=1, merge_type=UnspliceMergeType.TAKE_CENTER_FRAME):
        self.splice_size = splice_size
        self.splice_step = splice_step
        self.merge_type = merge_type

    def process(self, feature_matrix):
        if self.merge_type == UnspliceMergeType.COMPUTE_MEAN:
            return array.unsplice_features(feature_matrix, self.splice_size, self.splice_step)
        elif self.merge_type == UnspliceMergeType.TAKE_CENTER_FRAME:
            frame_len = np.size(feature_matrix, 1) // (self.splice_size * 2 + 1)
            start = self.splice_size * frame_len
            end = (self.splice_size + 1) * frame_len
            return feature_matrix[:, start:end]
