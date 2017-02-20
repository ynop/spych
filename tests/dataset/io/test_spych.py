import unittest
import tempfile
import shutil
import os

from spych.dataset import dataset
from spych.dataset import speaker
from spych.dataset.io import spych


class DatasetTest(unittest.TestCase):
    def setUp(self):
        self.loader = spych.SpychDatasetLoader()
        self.test_path = os.path.join(os.path.dirname(__file__), '..', 'spych_ds')

    def tearDown(self):
        pass

    def test_load(self):
        loaded_dataset = self.loader.load(self.test_path)

        self.assertEqual(4, loaded_dataset.num_files)
        self.assertEqual(5, loaded_dataset.num_utterances)
        self.assertEqual(3, loaded_dataset.num_speakers)

        self.assertIn('utt-4', loaded_dataset.utterances.keys())

        utterance = loaded_dataset.utterances['utt-4']

        self.assertEqual('file-3', utterance.file_idx)
        self.assertEqual(15, utterance.start)
        self.assertEqual(25, utterance.end)
        self.assertEqual('speaker-2', utterance.speaker_idx)

        self.assertIn('speaker-2', loaded_dataset.speakers.keys())

        spk = loaded_dataset.speakers['speaker-2']

        self.assertEqual(speaker.Gender.FEMALE, spk.gender)

        self.assertIn('utt-4', loaded_dataset.segmentations.keys())
        self.assertIn('text', loaded_dataset.segmentations['utt-4'].keys())
        self.assertIn('raw_text', loaded_dataset.segmentations['utt-4'].keys())

        self.assertEqual(3, len(loaded_dataset.segmentations['utt-4']['text'].segments))
        self.assertEqual('are', loaded_dataset.segmentations['utt-4']['text'].segments[1].value)

        self.assertEqual(3.5, loaded_dataset.segmentations['utt-4']['text'].segments[2].start)
        self.assertEqual(4.2, loaded_dataset.segmentations['utt-4']['text'].segments[2].end)
