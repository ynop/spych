class Subview(object):
    """
    A subview is a filtered view on a dataset. For example it only uses a subset of utterance-id's.
    """

    def __init__(self, filtered_utterances=set(), filtered_speakers=set(), dataset=None):
        self.dataset = dataset

        self.filtered_utterance_idxs = set(filtered_utterances)
        self.filtered_speaker_idxs = set(filtered_speakers)

    @property
    def files(self):
        return {utterance.file_idx: self.dataset.files[utterance.file_idx] for utterance in self.utterances.values()}

    @property
    def utterances(self):
        filtered_utterances = {}

        for utterance_idx, utterance in self.dataset.utterances.items():
            if (len(self.filtered_utterance_idxs) <= 0 or utterance_idx in self.filtered_utterance_idxs) \
                    and (len(self.filtered_speaker_idxs) <= 0 or utterance.speaker_idx in self.filtered_speaker_idxs):
                filtered_utterances[utterance_idx] = utterance

        return filtered_utterances

    @property
    def speakers(self):
        return {utterance.speaker_idx: self.dataset.speakers[utterance.speaker_idx] for utterance in self.utterances.values()}

    @property
    def segmentations(self):
        return {utterance.idx: dict(self.dataset.segmentations[utterance.idx]) for utterance in self.utterances.values()}
