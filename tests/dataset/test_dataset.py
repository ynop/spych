import unittest
import tempfile
import shutil
import os

from spych.dataset import dataset


class DatasetTest(unittest.TestCase):
    def setUp(self):
        self.dataset_path = tempfile.mkdtemp()

        self.dataset = dataset.Dataset(self.dataset_path)

    def tearDown(self):
        shutil.rmtree(self.dataset_path, ignore_errors=True)

    def test_name(self):
        self.assertEqual(os.path.basename(self.dataset_path), self.dataset.name)

    def test_add_file(self):
        file_path = os.path.join(os.path.dirname(__file__), 'wav_1.wav')

        file_obj = self.dataset.add_file(file_path)

        self.assertEqual(os.path.relpath(file_path, self.dataset_path), file_obj.path)
        self.assertIsNotNone(file_obj.idx)
        self.assertEqual(file_obj, self.dataset.files[file_obj.idx])

    def test_add_file_with_id(self):
        file_path = os.path.join(os.path.dirname(__file__), 'wav_1.wav')

        file_obj = self.dataset.add_file(file_path, file_idx='file_id_1')

        self.assertEqual(os.path.relpath(file_path, self.dataset_path), file_obj.path)
        self.assertEqual('file_id_1', file_obj.idx)
        self.assertEqual(file_obj, self.dataset.files[file_obj.idx])

    def test_add_file_with_copy(self):
        file_path = os.path.join(os.path.dirname(__file__), 'wav_1.wav')

        file_obj = self.dataset.add_file(file_path, copy_file=True)

        self.assertEqual('wav_1.wav', file_obj.path)
        self.assertIsNotNone(file_obj.idx)
        self.assertEqual(file_obj, self.dataset.files[file_obj.idx])

    def test_add_utterance(self):
        file_path = os.path.join(os.path.dirname(__file__), 'wav_1.wav')
        file_obj = self.dataset.add_file(file_path)

        utt_obj = self.dataset.add_utterance(file_obj.idx)

        self.assertEqual(file_obj.idx, utt_obj.file_idx)
        self.assertEqual(utt_obj, self.dataset.utterances[utt_obj.idx])

    def test_add_speaker(self):
        spk_obj = self.dataset.add_speaker()

        self.assertIsNotNone(spk_obj.idx)
        self.assertEqual(spk_obj, self.dataset.speakers[spk_obj.idx])

    def test_add_segmentation(self):
        file_path = os.path.join(os.path.dirname(__file__), 'wav_1.wav')
        file_obj = self.dataset.add_file(file_path)

        utt_obj = self.dataset.add_utterance(file_obj.idx)

        seg_obj = self.dataset.add_segmentation(utt_obj.idx, segments='who am i')

        self.assertEqual(utt_obj.idx, seg_obj.utterance_idx)
        self.assertEqual('text', seg_obj.key)
        self.assertEqual(3, len(seg_obj.segments))

        self.assertEqual(seg_obj, self.dataset.segmentations[utt_obj.idx][seg_obj.key])
