import enum

from spych.data import dataset
from spych.audio import format as audio_format


class RectificationTask(enum.Enum):
    REMOVE_MISSING_FILES = 'remove_files_missing'
    REMOVE_FILES_WITH_WRONG_FORMAT = 'remove_files_with_wrong_format'
    REMOVE_ZERO_LENGTH_FILES = 'remove_files_with_zero_length'
    REMOVE_UTTERANCES_WITHOUT_FILE_ID = 'remove_utterance_without_file_id'


class Rectifier(object):
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

    def rectify(self, dataset_to_fix):
        if RectificationTask.REMOVE_MISSING_FILES in self.tasks:
            Rectifier.remove_files_missing(dataset_to_fix)

        if RectificationTask.REMOVE_FILES_WITH_WRONG_FORMAT in self.tasks:
            Rectifier.remove_files_with_wrong_format(dataset_to_fix)

        if RectificationTask.REMOVE_ZERO_LENGTH_FILES in self.tasks:
            Rectifier.remove_empty_wavs(dataset_to_fix)

        if RectificationTask.REMOVE_UTTERANCES_WITHOUT_FILE_ID in self.tasks:
            Rectifier.remove_utterances_with_missing_file(dataset_to_fix)

    @staticmethod
    def remove_files_missing(self, dataset_to_fix):
        """ Delete all files references, where the referenced wav file doesn't exist. """
        files_missing = dataset.Validator.get_files_missing(dataset_to_fix)
        dataset_to_fix.remove_wavs(files_missing, remove_files=False)
        dataset_to_fix.save()

    @staticmethod
    def remove_empty_wavs(self, dataset_to_fix):
        """ Delete all files that have no content. """
        empty_files = dataset.Validator.get_files_empty(dataset_to_fix)
        dataset_to_fix.remove_wavs(empty_files, remove_files=True)
        dataset_to_fix.save()

    @staticmethod
    def remove_files_with_wrong_format(self, dataset_to_fix, expected_format=audio_format.AudioFileFormat.wav_mono_16bit_16k()):
        """ Delete all wav files with the wrong format (Sampling rate, sample width, ...). """
        wrong_files = dataset.Validator.get_files_with_wrong_format(dataset_to_fix, expected_format)
        dataset_to_fix.remove_wavs(wrong_files, remove_files=True)
        dataset_to_fix.save()

    @staticmethod
    def remove_utterances_with_missing_file(self, dataset_to_fix):
        """ Remove all utterances where the referenced file doesn't exist. """
        utts = dataset.Validator.get_utterances_with_missing_file_idx(dataset_to_fix)
        dataset_to_fix.remove_utterances(utts)
        dataset_to_fix.save()
