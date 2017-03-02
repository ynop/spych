class Utterance(object):
    __slots__ = ['idx', 'file_idx', 'speaker_idx', 'start', 'end']

    START_FULL_FILE = 0
    END_FULL_FILE = -1

    def __init__(self, idx, file_idx, speaker_idx=None, start=START_FULL_FILE, end=END_FULL_FILE):
        self.idx = idx
        self.file_idx = file_idx
        self.speaker_idx = speaker_idx
        self.start = start
        self.end = end
