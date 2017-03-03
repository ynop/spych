import re


class Subview(object):
    """
    A subview is a filtered view on a dataset. For example it only uses a subset of utterance-id's.
    """

    def __init__(self, filtered_utterances=set(), filtered_speakers=set(), dataset=None):
        self.dataset = dataset

        self.filtered_utterance_idxs = set(filtered_utterances)
        self.filtered_speaker_idxs = set(filtered_speakers)

        self.utterance_idx_patterns = set()
        self.speaker_idx_patterns = set()

        self.utterance_idx_not_patterns = set()
        self.speaker_idx_not_patterns = set()

    @property
    def files(self):
        return {utterance.file_idx: self.dataset.files[utterance.file_idx] for utterance in self.utterances.values()}

    @property
    def utterances(self):
        filtered_utterances = {}

        for utterance_idx, utterance in self.dataset.utterances.items():
            if self.does_utterance_match(utterance):
                filtered_utterances[utterance_idx] = utterance

        return filtered_utterances

    @property
    def speakers(self):
        return {utterance.speaker_idx: self.dataset.speakers[utterance.speaker_idx] for utterance in self.utterances.values()}

    @property
    def segmentations(self):
        return {utterance.idx: dict(self.dataset.segmentations[utterance.idx]) for utterance in self.utterances.values()}

    @property
    def features(self):
        return self.dataset.features

    def does_utterance_match(self, utterance):
        """ Return True if the given utterance matches all filter criteria. Otherwise return False. """

        if len(self.filtered_utterance_idxs) > 0 and utterance.idx not in self.filtered_utterance_idxs:
            return False

        if len(self.filtered_speaker_idxs) > 0 and utterance.speaker_idx not in self.filtered_speaker_idxs:
            return False

        for utt_id_pattern in self.utterance_idx_patterns:
            if not re.fullmatch(utt_id_pattern, utterance.idx):
                return False

        for spk_id_pattern in self.speaker_idx_patterns:
            if not re.fullmatch(spk_id_pattern, utterance.speaker_idx):
                return False

        for utt_id_pattern in self.utterance_idx_not_patterns:
            if re.fullmatch(utt_id_pattern, utterance.idx):
                return False

        for spk_id_pattern in self.speaker_idx_not_patterns:
            if re.fullmatch(spk_id_pattern, utterance.speaker_idx):
                return False

        return True
