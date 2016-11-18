import random
import copy
import collections
import re

from spych.data import dataset
from spych.utils import math


class DatasetSplitter(object):
    def __init__(self, dataset):
        self.dataset = dataset

    def split(self, subset_config={}, split_speakers=False, copy_wavs=False):
        """
        Splits the dataset according to the given proportions. Proportions should sum to 1.0.

        subset_config:
        {
            [subset_path] : [proportion],
            "/path/to/set" : 0.3
        }

        :param subset_config: Configuration for splitting
        :param split_speakers: If True looks that one speaker only occurs in one subset.
        :param copy_wavs: If True, copies the wav files to the subsets folder
        :return: dict subset/proportion
        """

        subsets = {}

        if split_speakers:
            utterance_splits = self._get_utterances_splitted_by_speaker(subset_config)
        else:
            utterance_splits = self._get_utterances_randomly_splitted(subset_config)

        total_utterances = 0

        for utterances in utterance_splits.values():
            total_utterances += len(utterances)

        for subset_path, utterance_ids in utterance_splits.items():
            subset = self.get_subset_with_utterances(subset_path, utterance_ids, copy_wavs=copy_wavs)
            subsets[subset] = float(len(utterance_ids)) / float(total_utterances)

        return subsets

    def create_subset_with_filtered_utterances(self, path, utterance_filter, copy_wavs=False):
        """
        Creates a subset with all utterances matching the given filter.

        :param path: Path to store the subset.
        :param utterance_filter: Filter (Regex)
        :param copy_wavs: If True, copies the wav files to the subsets folder
        :return: Subset
        """
        matching_utt_ids = []

        pattern = re.compile(utterance_filter)

        for utt_id in self.dataset.utterances.keys():
            match = pattern.fullmatch(utt_id)

            if match is not None:
                matching_utt_ids.append(utt_id)

        subset = self.get_subset_with_utterances(path, matching_utt_ids, copy_wavs=copy_wavs)
        return subset

    def create_subset_with_filtered_speakers(self, path, speaker_filter, copy_wavs=False):
        """
        Creates a subset with all speakers matching the given filter.

        :param path: Path to store the subset.
        :param speaker_filter: Filter (Regex)
        :param copy_wavs: If True, copies the wav files to the subsets folder
        :return: Subset
        """
        matching_utt_ids = []
        spk2utt = self.dataset.get_speaker_to_utterances()

        pattern = re.compile(speaker_filter)

        for speaker_id in self.dataset.all_speakers():
            match = pattern.fullmatch(speaker_id)

            if match is not None:
                matching_utt_ids.extend(spk2utt[speaker_id])

        subset = self.get_subset_with_utterances(path, matching_utt_ids, copy_wavs=copy_wavs)
        return subset

    def get_subset_with_utterances(self, path, utterance_ids, copy_wavs=False):
        """
        Creates subset at given path with the given utterance-ids.

        :param path: Path for subset
        :param utterance_ids: List of utterance-ids
        :param copy_wavs: If True, copies the wav files to the subsets folder
        :return: subset
        """

        wavs = {}
        utterances = {}
        transcriptions = {}
        transcriptions_raw = {}
        utt2spk = {}
        speaker_info = {}

        subset = dataset.Dataset(dataset_folder=path)
        subset.save()

        for utt_id in utterance_ids:
            utterances[utt_id] = list(self.dataset.utterances[utt_id])

            wav_id = utterances[utt_id][0]
            wavs[wav_id] = self.dataset.wavs[wav_id]

            if self.dataset.utterance_has_transcription(utt_id):
                transcriptions[utt_id] = self.dataset.transcriptions[utt_id]

            if self.dataset.utterance_has_transcription_raw(utt_id):
                transcriptions_raw[utt_id] = self.dataset.transcriptions_raw[utt_id]

            if self.dataset.utterance_has_speaker(utt_id):
                utt2spk[utt_id] = self.dataset.utt2spk[utt_id]
                speaker_id = utt2spk[utt_id]

                if self.dataset.speaker_has_info(speaker_id):
                    speaker_info[speaker_id] = copy.deepcopy(self.dataset.speaker_info[speaker_id])

        wav_id_mapping = subset.import_wavs(wavs, base_path=self.dataset.path, copy_files=False)
        utt_id_mapping = subset.add_utterances(utterances, wav_id_mapping=wav_id_mapping)
        speaker_id_mapping = subset.add_speaker_info(speaker_info)
        subset.set_transcriptions(transcriptions, utt_id_mapping=utt_id_mapping)
        subset.set_utt2spk(utt2spk, utt_id_mapping=utt_id_mapping, speaker_id_mapping=speaker_id_mapping)
        subset.set_transcriptions_raw(transcriptions_raw, utt_id_mapping=utt_id_mapping)

        subset.save()

        return subset

    def _get_utterances_splitted_by_speaker(self, subset_config={}):
        """
        Get utterances splitted by speakers, trying to split with the given proportions.

        :param subset_config: Proportions
        :return: dict path:[list of utterances]
        """

        spk2utt = self.dataset.get_speaker_to_utterances()

        if len(spk2utt) < len(subset_config):
            raise ValueError("There are not enough speakers ({}) to split into {} subsets.".format(len(spk2utt), len(subset_config)))

        spk2utt_count = {speaker_id: len(utterances) for speaker_id, utterances in spk2utt.items()}

        subset_to_speaker_id = math.try_distribute_values_proportionally(spk2utt_count, subset_config)

        utterance_id_splits = collections.defaultdict(list)

        for subset_path, speaker_ids in subset_to_speaker_id.items():
            for speaker_id in speaker_ids:
                utterance_id_splits[subset_path].extend(spk2utt[speaker_id])

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
