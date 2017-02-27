import enum

from spych.dataset import validation
from spych.audio import format as audio_format


class RectificationTask(enum.Enum):
    REMOVE_MISSING_FILES = 'remove_files_missing'
    REMOVE_FILES_WITH_WRONG_FORMAT = 'remove_files_with_wrong_format'
    REMOVE_ZERO_LENGTH_FILES = 'remove_files_with_zero_length'
    REMOVE_UTTERANCES_WITHOUT_FILE_ID = 'remove_utterance_without_file_id'


class DatasetRectifier(object):
    """
    Provides functionality to fix invalid dataset parts.
    """

    def __init__(self, tasks=[], expected_file_format=audio_format.AudioFileFormat.wav_mono_16bit_16k()):
        self.tasks = list(tasks)
        self.file_format = expected_file_format

    @classmethod
    def full_rectifier(cls, expected_file_format=audio_format.AudioFileFormat.wav_mono_16bit_16k()):
        return cls(tasks=[RectificationTask.REMOVE_MISSING_FILES,
                          RectificationTask.REMOVE_FILES_WITH_WRONG_FORMAT,
                          RectificationTask.REMOVE_ZERO_LENGTH_FILES,
                          RectificationTask.REMOVE_UTTERANCES_WITHOUT_FILE_ID],
                   expected_file_format=expected_file_format)

    def rectify(self, dataset):
        if RectificationTask.REMOVE_MISSING_FILES in self.tasks:
            DatasetRectifier.remove_files_missing(dataset)

        if RectificationTask.REMOVE_FILES_WITH_WRONG_FORMAT in self.tasks:
            DatasetRectifier.remove_files_with_wrong_format(dataset)

        if RectificationTask.REMOVE_ZERO_LENGTH_FILES in self.tasks:
            DatasetRectifier.remove_empty_wavs(dataset)

        if RectificationTask.REMOVE_UTTERANCES_WITHOUT_FILE_ID in self.tasks:
            DatasetRectifier.remove_utterances_with_missing_file(dataset)

    @staticmethod
    def remove_files_missing(self, dataset):
        """ Delete all files references, where the referenced wav file doesn't exist. """
        files_missing = validation.DatasetValidator.get_files_missing(dataset)
        dataset.remove_wavs(files_missing, remove_files=False)
        dataset.save()

    @staticmethod
    def remove_empty_wavs(self, dataset):
        """ Delete all files that have no content. """
        empty_files = validation.DatasetValidator.get_files_empty(dataset)
        dataset.remove_wavs(empty_files, remove_files=True)
        dataset.save()

    @staticmethod
    def remove_files_with_wrong_format(self, dataset, expected_format=audio_format.AudioFileFormat.wav_mono_16bit_16k()):
        """ Delete all wav files with the wrong format (Sampling rate, sample width, ...). """
        wrong_files = validation.DatasetValidator.get_files_with_wrong_format(dataset, expected_format)
        dataset.remove_wavs(wrong_files, remove_files=True)
        dataset.save()

    @staticmethod
    def remove_utterances_with_missing_file(self, dataset):
        """ Remove all utterances where the referenced file doesn't exist. """
        utts = validation.DatasetValidator.get_utterances_with_missing_file_idx(dataset)
        dataset.remove_utterances(utts)
        dataset.save()
