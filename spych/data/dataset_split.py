import random
import copy
import collections
import operator
import re

from spych.data import dataset
from spych.utils import math


class DatasetSplitter(object):
    def __init__(self, dataset):
        self.dataset = dataset

    def split(self, subset_config={}, split_by_speakers=False, speaker_divided=False, copy_wavs=False):
        """
        Splits the dataset according to the given proportions. Proportions should sum to 1.0.

        subset_config:
        {
            [subset_path] : [proportion],
            "/path/to/set" : 0.3
        }

        :param subset_config: Configuration for splitting
        :param split_by_speakers: If True splits proportionally by speakers otherwise by utterances.
        :param speaker_divided: Only when split_by_speakers=False, makes sure one speaker only occurs in one subset.
        :param copy_wavs: If True, copies the wav files to the subsets folder
        :return: dict subset/proportion
        """

        subsets = {}

        if split_by_speakers:
            utterance_splits = self._get_utterances_splitted_by_speaker(subset_config)
        else:
            if speaker_divided:
                utterance_splits = self._get_utterances_splitted_speaker_separated(subset_config)
            else:
                utterance_splits = self._get_utterances_randomly_splitted(subset_config)

        total_utterances = 0

        for utterances in utterance_splits.values():
            total_utterances += len(utterances)

        for subset_path, utterance_ids in utterance_splits.items():
            subset = self.get_subset_with_utterances(subset_path, utterance_ids, copy_wavs=copy_wavs)
            subsets[subset] = float(len(utterance_ids)) / float(total_utterances)

        return subsets

    def create_subset_with_filtered_utterances(self, path, utterance_filter, max_items=-1, inverse=False, copy_wavs=False):
        """
        Creates a subset with all utterances matching the given filter.

        :param path: Path to store the subset.
        :param utterance_filter: Filter (Regex)
        :param max_items: max number of utterances
        :param inverse: If True returns utterances that do not match filter.
        :param copy_wavs: If True, copies the wav files to the subsets folder
        :return: Subset
        """
        matching_utt_ids = []

        pattern = re.compile(utterance_filter)

        index = 0
        count = 0
        utterance_ids = list(self.dataset.utterances.keys())

        while index < len(utterance_ids) and (max_items == -1 or count <= max_items):
            utt_id = utterance_ids[index]
            match = pattern.fullmatch(utt_id)

            if (match is not None and not inverse) or (match is None and inverse):
                matching_utt_ids.append(utt_id)
                count += 1

            index += 1

        subset = self.get_subset_with_utterances(path, matching_utt_ids, copy_wavs=copy_wavs)
        return subset

    def create_subset_with_filtered_speakers(self, path, speaker_filter, max_items=-1, inverse=False, copy_wavs=False):
        """
        Creates a subset with all speakers matching the given filter.

        :param path: Path to store the subset.
        :param speaker_filter: Filter (Regex)
        :param max_items: max number of speakers
        :param inverse: If True returns speakers that do not match filter.
        :param copy_wavs: If True, copies the wav files to the subsets folder
        :return: Subset
        """
        matching_utt_ids = set()

        pattern = re.compile(speaker_filter)

        index = 0
        count = 0
        speaker_ids = list(self.dataset.all_speakers())

        while index < len(speaker_ids) and (max_items == -1 or count <= max_items):
            speaker_id = speaker_ids[index]
            match = pattern.fullmatch(speaker_id)

            if (match is not None and not inverse) or (match is None and inverse):
                matching_utt_ids.update(self.dataset.utterances_of_speaker(speaker_id))
                count += 1

            index += 1

        subset = self.get_subset_with_utterances(path, matching_utt_ids, copy_wavs=copy_wavs)
        return subset

    def create_subset_with_filtered_transcriptions(self, path, passing_transcriptions, max_items=-1, inverse=False, copy_wavs=False):
        """
        Creates a subset with all utterances that have a transcription that is in the passing_transcriptions list.

        :param path: Path to store the subset.
        :param passing_transcriptions: List of transcriptions to filter.
        :param max_items: max number of utterances.
        :param inverse: if True, transcriptions that are not in the passing_transcriptions list are returned.
        :param copy_wavs: If True, copies the wav files to the subsets folder
        :return: Subset
        """
        matching_utt_ids = set()

        index = 0
        count = 0
        utterance_ids = list(self.dataset.transcriptions.keys())

        while index < len(utterance_ids) and (max_items == -1 or count <= max_items):
            utt_id = utterance_ids[index]
            transcription = self.dataset.transcriptions[utt_id]

            if (transcription in passing_transcriptions and not inverse) or (transcription not in passing_transcriptions and inverse):
                matching_utt_ids.add(utt_id)
                count += 1

            index += 1

        subset = self.get_subset_with_utterances(path, matching_utt_ids, copy_wavs=copy_wavs)
        return subset

    def create_subset_with_random_utterances(self, path, num_utterances, copy_wavs=False):
        """
        Create a subset with the given number of utterances, random picked.

        :param path: Path to store the subset.
        :param num_utterances: Number of utterances to pick.
        :param copy_wavs: If True, copies the wav files to the subsets folder
        :return: Subset
        """
        if num_utterances < 0:
            count = random.randint(1, len(self.dataset.utterances))
        else:
            count = num_utterances

        utterance_ids = random.sample(self.dataset.utterances.keys(), count)

        return self.get_subset_with_utterances(path, utterance_ids, copy_wavs=copy_wavs)

    def create_subset_with_random_speakers(self, path, num_speakers, copy_wavs=False):
        """
        Create a subset with the given number of speakers, random picked.

        :param path: Path to store the subset.
        :param num_speakers: Number of speakers to pick.
        :param copy_wavs: If True, copies the wav files to the subsets folder
        :return: Subset
        """
        if num_speakers < 0:
            count = random.randint(1, len(self.dataset.all_speakers()))
        else:
            count = num_speakers

        speaker_ids = random.sample(self.dataset.all_speakers(), count)
        utterance_ids = set()

        for speaker_id in speaker_ids:
            utterance_ids.update(self.dataset.utterances_of_speaker(speaker_id))

        return self.get_subset_with_utterances(path, utterance_ids, copy_wavs=copy_wavs)

    def get_subset_with_utterances(self, path, utterance_ids, copy_wavs=False):
        """
        Creates subset at given path with the given utterance-ids.

        :param path: Path for subset
        :param utterance_ids: List/Set of utterance-ids
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

    # def _get_utterances_splitted_by_speaker(self, subset_config={}):
    #     """
    #     Get utterances splitted by speakers. First prio is to split speakers by the given proportions.
    #     Afterwards trying to split so that nr utterances are distributed according the given proportions.
    #
    #     :param subset_config: Proportions
    #     :return: dict path:[list of utterances]
    #     """
    #
    #     spk2utt = self.dataset.get_speaker_to_utterances()
    #
    #     if len(spk2utt) < len(subset_config):
    #         raise ValueError("There are not enough speakers ({}) to split into {} subsets.".format(len(spk2utt), len(subset_config)))
    #
    #     spk2utt_count = {speaker_id: len(utterances) for speaker_id, utterances in spk2utt.items()}
    #     spk2utt_count_sorted = collections.OrderedDict(sorted(spk2utt_count.items(), key=operator.itemgetter(1), reverse=True))
    #
    #     proportions = math.calculate_absolute_proportions(len(spk2utt), subset_config)
    #
    #     spk_id_splits = collections.defaultdict(list)
    #
    #     for spk_id, utt_count in spk2utt_count_sorted.items():

    def _get_utterances_splitted_by_speaker(self, subset_config={}):
        """
        Get utterances splitted by speakers. First prio is to split speakers by the given proportions.

        :param subset_config: Proportions
        :return: dict path:[list of utterances]
        """

        spk2utt = self.dataset.get_speaker_to_utterances()

        if len(spk2utt) < len(subset_config):
            raise ValueError("There are not enough speakers ({}) to split into {} subsets.".format(len(spk2utt), len(subset_config)))

        proportions = math.calculate_absolute_proportions(len(spk2utt), subset_config)

        speakers = list(spk2utt.keys())
        random.shuffle(speakers)

        utterance_id_splits = collections.defaultdict(list)
        start_index = 0

        for path, proportion in proportions.items():
            selected_speakers = speakers[start_index:start_index + proportion]

            for speaker in selected_speakers:
                utterance_id_splits[path].extend(spk2utt[speaker])

            start_index += proportion

        return utterance_id_splits

    def _get_utterances_splitted_speaker_separated(self, subset_config={}):
        """
        Get utterances splitted, trying to split with the given proportions so that one speaker only appears in one subset.

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
