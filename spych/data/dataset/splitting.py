import collections
import random

from spych.utils import math
from spych.data import dataset


class Splitter(object):

    def __init__(self, dataset):
        self.dataset = dataset

    def split(self, subset_config={}, split_by_speakers=False, speaker_divided=False):
        """
        Splits the dataset according to the given proportions. Proportions should sum to 1.0.

        subset_config:
        {
            name : proportion,
            "train" : 0.3
        }

        :param subset_config: Configuration for splitting
        :param split_by_speakers: If True splits proportionally by speakers otherwise by utterances.
        :param speaker_divided: Only when split_by_speakers=False, makes sure one speaker only occurs in one subset.
        :return: dict name/subview
        """

        subsets = {}

        if split_by_speakers:
            utterance_splits = self._get_utterances_splitted_by_speaker(subset_config)
        else:
            if speaker_divided:
                utterance_splits = self._get_utterances_splitted_speaker_separated(subset_config)
            else:
                utterance_splits = self._get_utterances_randomly_splitted(subset_config)

        for name, utterance_ids in utterance_splits.items():
            subsets[name] = dataset.Subview(filtered_utterances=set(utterance_ids), dataset=self.dataset)

        return subsets

    def _get_utterances_splitted_by_speaker(self, subset_config={}):
        """
        Get utterances splitted by speakers. First prio is to split speakers by the given proportions.

        :param subset_config: Proportions
        :return: dict path:[list of utterances]
        """

        if self.dataset.num_speakers < len(subset_config):
            raise ValueError("There are not enough speakers ({}) to split into {} subsets.".format(self.dataset.num_speakers, len(subset_config)))

        proportions = math.calculate_absolute_proportions(self.dataset.num_speakers, subset_config)

        speakers = list(self.dataset.speakers.keys())
        random.shuffle(speakers)

        utterance_id_splits = collections.defaultdict(list)
        start_index = 0

        for path, proportion in proportions.items():
            selected_speakers = speakers[start_index:start_index + proportion]

            for speaker in selected_speakers:
                utts = self.dataset.utterances_of_speaker(speaker)
                utterance_id_splits[path].extend([utt.idx for utt in utts])

            start_index += proportion

        return utterance_id_splits

    def _get_utterances_splitted_speaker_separated(self, subset_config={}):
        """
        Get utterances splitted, trying to split with the given proportions so that one speaker only appears in one subset.

        :param subset_config: Proportions
        :return: dict path:[list of utterances]
        """

        if self.dataset.num_speakers < len(subset_config):
            raise ValueError("There are not enough speakers ({}) to split into {} subsets.".format(self.dataset.num_speakers, len(subset_config)))

        spk2utt = self.dataset.speaker_to_utterance_dict()
        spk2utt_count = {speaker.idx: len(utterances) for speaker, utterances in spk2utt.items()}

        subset_to_speaker_id = math.try_distribute_values_proportionally(spk2utt_count, subset_config)

        utterance_id_splits = collections.defaultdict(list)

        for subset_path, speaker_ids in subset_to_speaker_id.items():
            for speaker_id in speaker_ids:
                utts = self.dataset.utterances_of_speaker(speaker_id)
                utterance_id_splits[subset_path].extend([utt.idx for utt in utts])

        return utterance_id_splits

    def _get_utterances_randomly_splitted(self, subset_config={}):
        """
        Get randomly splitted utterance with the given proportions.

        :param subset_config: Proportions
        :return: dict path:[list of utterances]
        """
        proportions = math.calculate_absolute_proportions(len(self.dataset.utterances), subset_config)

        utterances = list(self.dataset.utterances.keys())
        random.shuffle(utterances)

        utterance_id_splits = {}
        start_index = 0

        for path, proportion in proportions.items():
            utterance_id_splits[path] = utterances[start_index:start_index + proportion]
            start_index += proportion

        return utterance_id_splits
