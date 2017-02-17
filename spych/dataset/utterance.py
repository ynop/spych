START_FULL_FILE = 0
END_FULL_FILE = -1


class Utterance(object):
    __slots__ = ['idx', 'file_idx', 'speaker_idx', 'start', 'end']

    def __init__(self, idx, file_idx, speaker_idx=None, start=0, end=-1):
        self.idx = idx
        self.file_idx = file_idx
        self.speaker_idx = speaker_idx
        self.start = start
        self.end = end
