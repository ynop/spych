import os
import sndhdr
import enum
import collections
import glob

from spych import data
from spych.audio import format as audio_format


class ValidationMetric(enum.Enum):
    FILE_MISSING = 'file_missing'
    FILE_INVALID_FORMAT = 'file_invalid_format'
    FILE_ZERO_LENGTH = 'file_zero_length'
    FILE_NO_UTTERANCES = 'file_no_utterance'
    UTTERANCE_NO_FILE_ID = 'utterance_no_file_id'
    UTTERANCE_INVALID_START_END = 'utterance_invalid_start_end'
    UTTERANCE_MISSING_SPEAKER = 'utterance_missing_speaker'
    SPEAKER_MISSING_GENDER = 'speaker_missing_gender'
    SEGMENTATION_MISSING = 'segmentation_missing'
    FEATURE_MISSING = 'feature_missing'


class Validator(object):
    """
    Class to validate a dataset.
    """

    def __init__(self, metrics=[], expected_file_format=audio_format.AudioFileFormat.wav_mono_16bit_16k()):
        self.metrics = list(metrics)
        self.file_format = expected_file_format

    def validate(self, dataset):
        """ Return the validation results for the selected validation metrics. (dictionary metric/results) """

        results = {}

        if ValidationMetric.FILE_MISSING in self.metrics:
            results[ValidationMetric.FILE_MISSING] = Validator.get_files_missing(dataset)

        if ValidationMetric.FILE_INVALID_FORMAT in self.metrics:
            results[ValidationMetric.FILE_INVALID_FORMAT] = Validator.get_files_with_wrong_format(dataset, self.file_format)

        if ValidationMetric.FILE_ZERO_LENGTH in self.metrics:
            results[ValidationMetric.FILE_ZERO_LENGTH] = Validator.get_files_empty(dataset)

        if ValidationMetric.FILE_NO_UTTERANCES in self.metrics:
            results[ValidationMetric.FILE_NO_UTTERANCES] = Validator.get_files_without_utterances(dataset)

        if ValidationMetric.UTTERANCE_NO_FILE_ID in self.metrics:
            results[ValidationMetric.UTTERANCE_NO_FILE_ID] = Validator.get_utterances_with_missing_file_idx(dataset)

        if ValidationMetric.UTTERANCE_INVALID_START_END in self.metrics:
            results[ValidationMetric.UTTERANCE_INVALID_START_END] = Validator.get_utterances_with_invalid_start_end(dataset)

        if ValidationMetric.UTTERANCE_MISSING_SPEAKER in self.metrics:
            results[ValidationMetric.UTTERANCE_MISSING_SPEAKER] = Validator.get_utterances_with_missing_speaker(dataset)

        if ValidationMetric.SEGMENTATION_MISSING in self.metrics:
            results[ValidationMetric.SEGMENTATION_MISSING] = Validator.get_utterances_without_segmentation(dataset)

        if ValidationMetric.SPEAKER_MISSING_GENDER in self.metrics:
            results[ValidationMetric.SPEAKER_MISSING_GENDER] = Validator.get_speakers_without_gender(dataset)

        if ValidationMetric.FEATURE_MISSING in self.metrics:
            results[ValidationMetric.FEATURE_MISSING] = Validator.get_features_with_missing_file(dataset)

        return results

    @classmethod
    def full_validator(cls, expected_file_format=audio_format.AudioFileFormat.wav_mono_16bit_16k()):
        """ Returns a validator, that checks all metrics. """
        return cls(
            metrics=[
                ValidationMetric.FILE_MISSING,
                ValidationMetric.FILE_INVALID_FORMAT,
                ValidationMetric.FILE_ZERO_LENGTH,
                ValidationMetric.FILE_NO_UTTERANCES,
                ValidationMetric.UTTERANCE_NO_FILE_ID,
                ValidationMetric.UTTERANCE_INVALID_START_END,
                ValidationMetric.UTTERANCE_MISSING_SPEAKER,
                ValidationMetric.SPEAKER_MISSING_GENDER,
                ValidationMetric.SEGMENTATION_MISSING,
                ValidationMetric.FEATURE_MISSING
            ],
            expected_file_format=expected_file_format
        )

    @staticmethod
    def get_files_missing(dataset):
        """ Return a list of file-idx's where the actual file is missing. """
        missing_wavs = []

        for file in dataset.files.values():
            full_path = os.path.abspath(os.path.join(dataset.path, file.path))

            if not os.path.isfile(full_path):
                missing_wavs.append(file.idx)

        return missing_wavs

    @staticmethod
    def get_files_empty(dataset):
        """ Return a list of file-idx's that contain no data. """
        empty_wavs = []

        for file in dataset.files.values():
            full_path = os.path.abspath(os.path.join(dataset.path, file.path))

            if os.path.isfile(full_path):
                result = sndhdr.what(full_path)

                if result is None or result.nframes <= 0:
                    empty_wavs.append(file.idx)

        return empty_wavs

    @staticmethod
    def get_files_with_wrong_format(dataset, expected_format=audio_format.AudioFileFormat.wav_mono_16bit_16k()):
        """ Return a list of file-idx's that don't conform the given audio format. """
        files_with_wrong_format = []

        for file in dataset.files.values():
            full_path = os.path.abspath(os.path.join(dataset.path, file.path))

            if os.path.isfile(full_path):
                result = sndhdr.what(full_path)

                if result is None or not expected_format.matches_sound_header(result):
                    files_with_wrong_format.append(file.idx)

        return files_with_wrong_format

    @staticmethod
    def get_files_without_utterances(dataset):
        """ Return a list of file-idx's that don't reference any utterances.
        """
        files_with_utterances = set()

        for utterance in dataset.utterances.values():
            files_with_utterances.add(utterance.file_idx)

        files_without_utterances = list(set(dataset.files.keys()) - files_with_utterances)

        return files_without_utterances

    @staticmethod
    def get_utterances_with_missing_file_idx(dataset):
        """ Return a list of utterances that reference a wav-id that isn't existing. """
        utterances_with_missing_wav_id = []

        for utterance in dataset.utterances.values():
            if utterance.file_idx not in dataset.files.keys():
                utterances_with_missing_wav_id.append(utterance.idx)

        return utterances_with_missing_wav_id

    @staticmethod
    def get_utterances_with_invalid_start_end(dataset):
        """
        Check if there are any utterances that have invalid start/end time.

        Must be:
            - float
            - can be empty --> 0 -1
            - end >= start
            - start >= 0
            - end >= 0 or end = -1

        :param dataset: Dataset to check.
        :return: List of utterance-ids with invalid start/end.
        """
        utterances_with_invalid_start_end = []

        for utterance in dataset.utterances.values():
            try:
                start = float(utterance.start)
                end = float(utterance.end)

                if start < 0 or (end != -1 and (end <= 0 or start >= end)):
                    utterances_with_invalid_start_end.append(utterance.idx)
            except ValueError:
                utterances_with_invalid_start_end.append(utterance.idx)

        return utterances_with_invalid_start_end

    @staticmethod
    def get_utterances_without_segmentation(dataset):
        """ Return a dictionary of key/utterance-idx's where no segmentation is available. """

        keys = dataset.all_segmentation_keys
        missing_empty_transcriptions = {}

        for key in keys:
            missing_empty_transcriptions[key] = []

            for utterance in dataset.utterances.values():
                if utterance.idx not in dataset.segmentations.keys() or \
                                key not in dataset.segmentations[utterance.idx].keys() or \
                                len(dataset.segmentations[utterance.idx][key].segments) <= 0:
                    missing_empty_transcriptions[key].append(utterance.idx)

        return missing_empty_transcriptions

    @staticmethod
    def get_utterances_with_missing_speaker(dataset):
        """ Return list without or invalid speaker. """
        missing_empty_speakers = []

        for utterance in dataset.utterances.values():
            if utterance.speaker_idx is None or utterance.speaker_idx not in dataset.speakers.keys():
                missing_empty_speakers.append(utterance.idx)

        return missing_empty_speakers

    @staticmethod
    def get_speakers_without_gender(dataset):
        """ Return a list of speaker-idx's, where the gender is not defined. """
        missing_empty_genders = []

        for spk in dataset.speakers.values():
            if spk.gender not in [data.Gender.MALE, data.Gender.FEMALE]:
                missing_empty_genders.append(spk.idx)

        return missing_empty_genders

    @staticmethod
    def get_features_with_missing_file(dataset):
        """ Return a dictionary (feature-container, list of missing utterance-ids) where there is no feature file. """

        missing_feature_files = collections.defaultdict(list)
        needed_utterance_ids = set(dataset.utterances.keys())

        for name, container in dataset.features.items():
            utterance_ids = glob.glob(os.path.join(container.path, '*.npy'))
            utterance_ids = set([os.path.splitext(os.path.basename(x))[0] for x in utterance_ids])

            missing_feature_files[name] = list(needed_utterance_ids.difference(utterance_ids))

        return missing_feature_files
