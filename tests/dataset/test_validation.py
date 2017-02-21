import unittest
import shutil
import os

from spych.dataset import segmentation
from spych.dataset import validation

from . import resources


class DatasetTest(unittest.TestCase):
    def setUp(self):
        self.validator = validation.DatasetValidator.full_validator()

    def test_validate(self):
        validation_dataset = resources.create_invalid_dataset()

        result = self.validator.validate(validation_dataset)

        self.assertListEqual(['wav_2'], result[validation.ValidationMetric.FILE_MISSING])
        self.assertListEqual(['wav_4'], result[validation.ValidationMetric.FILE_INVALID_FORMAT])
        self.assertListEqual(['wav_3'], result[validation.ValidationMetric.FILE_ZERO_LENGTH])
        self.assertListEqual(['wav_4'], result[validation.ValidationMetric.FILE_NO_UTTERANCES])
        self.assertListEqual(['utt-4'], result[validation.ValidationMetric.UTTERANCE_NO_FILE_ID])
        self.assertListEqual(['utt-3'], result[validation.ValidationMetric.UTTERANCE_INVALID_START_END])
        self.assertListEqual(['utt-2'], result[validation.ValidationMetric.UTTERANCE_MISSING_SPEAKER])
        self.assertListEqual(['spk-3'], result[validation.ValidationMetric.SPEAKER_MISSING_GENDER])
        self.assertListEqual(['utt-2'], result[validation.ValidationMetric.SEGMENTATION_MISSING])

        shutil.rmtree(validation_dataset.path, ignore_errors=True)
