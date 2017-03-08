import os
import shutil
import tempfile
import unittest

from spych.data.dataset.io import spych
from spych.data import speaker

from tests.data import resources


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
        self.assertEqual(2, loaded_dataset.num_subviews)

        self.assertEqual('wav_1.wav', loaded_dataset.files['file-1'].path)

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

        self.assertIn('train', loaded_dataset.subviews.keys())

        view = loaded_dataset.subviews['train']

        self.assertSetEqual(set(['file-2', 'file-3']), set(view.files.keys()))
        self.assertSetEqual(set(['utt-2', 'utt-4']), set(view.utterances.keys()))
        self.assertSetEqual(set(['speaker-1', 'speaker-2']), set(view.speakers.keys()))

        self.assertIn('train_3', loaded_dataset.subviews.keys())

        view = loaded_dataset.subviews['train_3']

        self.assertSetEqual(set(['file-3']), set(view.files.keys()))
        self.assertSetEqual(set(['utt-4']), set(view.utterances.keys()))
        self.assertSetEqual(set(['speaker-2']), set(view.speakers.keys()))

        self.assertIn('mfcc', loaded_dataset.features.keys())
        self.assertIn('fbank', loaded_dataset.features.keys())

        self.assertEqual(os.path.join(loaded_dataset.path, 'mfcc_features'), loaded_dataset.features['mfcc'].path)
        self.assertEqual(os.path.join(loaded_dataset.path, 'fbank_features'), loaded_dataset.features['fbank'].path)

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