import unittest
import tempfile
import shutil
import os

from spych.dataset import dataset
from spych.dataset import speaker
from spych.dataset.io import spych

from .. import resources


class SpychDatasetLoaderTest(unittest.TestCase):
    def setUp(self):
        self.loader = spych.SpychDatasetLoader()
        self.test_path = resources.spych_dataset_path()

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

    def test_save(self):
        ds = resources.create_dataset()

        path = tempfile.mkdtemp()

        self.loader.save(ds, path)

        self.assertIn('files.txt', os.listdir(path))
        self.assertIn('utterances.txt', os.listdir(path))
        self.assertIn('speakers.json', os.listdir(path))
        self.assertIn('utt2spk.txt', os.listdir(path))
        self.assertIn('segmentation_text.txt', os.listdir(path))

        shutil.rmtree(path, ignore_errors=True)