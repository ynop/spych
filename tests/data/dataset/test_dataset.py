import os
import shutil
import unittest

from spych.data.dataset import subview

from tests.data import resources


class DatasetTest(unittest.TestCase):
    def setUp(self):
        self.dataset = resources.create_dataset()

    def tearDown(self):
        shutil.rmtree(self.dataset.path, ignore_errors=True)

    def test_name(self):
        self.assertEqual(os.path.basename(self.dataset.path), self.dataset.name)

    #
    #   Subview
    #
    def test_export_subview(self):
        filtered_utts = set(['utt-2', 'utt-4'])
        self.dataset.add_subview('test', subview.Subview(filtered_utterances=filtered_utts))

        exp_set = self.dataset.export_subview('test')

        self.assertSetEqual(set(['wav_2', 'wav_3']), set(exp_set.files.keys()))
        self.assertSetEqual(filtered_utts, set(exp_set.utterances.keys()))
        self.assertSetEqual(set([self.dataset.utterances['utt-2'].speaker_idx, 'spk-2']), set(exp_set.speakers.keys()))

    #
    #   File
    #

    def test_add_file(self):
        wav_path = resources.get_wav_file_path('wav_1.wav')
        file_obj = self.dataset.add_file(wav_path)

        self.assertEqual(os.path.abspath(wav_path), file_obj.path)
        self.assertIsNotNone(file_obj.idx)
        self.assertEqual(file_obj, self.dataset.files[file_obj.idx])

    def test_add_file_with_id(self):
        wav_path = resources.get_wav_file_path('wav_1.wav')
        file_obj = self.dataset.add_file(wav_path, file_idx='file_id_1')

        self.assertEqual(os.path.abspath(wav_path), file_obj.path)
        self.assertEqual('file_id_1', file_obj.idx)
        self.assertEqual(file_obj, self.dataset.files[file_obj.idx])

    def test_add_file_with_copy(self):
        wav_path = resources.get_wav_file_path('wav_1.wav')
        file_obj = self.dataset.add_file(wav_path, copy_file=True)

        self.assertEqual('audio_files/wav_1.wav', file_obj.path)
        self.assertIsNotNone(file_obj.idx)
        self.assertEqual(file_obj, self.dataset.files[file_obj.idx])

    def test_remove_files(self):
        self.dataset.remove_files(['wav_2', 'wav_3'])

        self.assertNotIn('wav_2', self.dataset.files)
        self.assertNotIn('wav_3', self.dataset.files)

        self.assertNotIn('utt-2', self.dataset.utterances)
        self.assertNotIn('utt-3', self.dataset.utterances)
        self.assertNotIn('utt-4', self.dataset.utterances)

        self.assertNotIn('utt-2', self.dataset.segmentations)
        self.assertNotIn('utt-3', self.dataset.segmentations)
        self.assertNotIn('utt-4', self.dataset.segmentations)

    #
    #   Utterance
    #

    def test_utterances_in_file(self):
        self.assertEqual(2, len(self.dataset.utterances_in_file('wav_3')))
        self.assertEqual(1, len(self.dataset.utterances_in_file('wav_4')))

    def test_utterances_of_speaker(self):
        self.assertEqual(2, len(self.dataset.utterances_of_speaker('spk-2')))
        self.assertEqual(1, len(self.dataset.utterances_of_speaker('spk-3')))

    def test_add_utterance(self):
        utt_obj = self.dataset.add_utterance('wav_2')

        self.assertEqual('wav_2', utt_obj.file_idx)
        self.assertEqual(utt_obj, self.dataset.utterances[utt_obj.idx])

    def test_remove_utterances(self):
        self.dataset.remove_utterances(['utt-2', 'utt-4'])

        self.assertNotIn('utt-2', self.dataset.utterances)
        self.assertNotIn('utt-4', self.dataset.utterances)

        self.assertNotIn('utt-2', self.dataset.segmentations)
        self.assertNotIn('utt-4', self.dataset.segmentations)

    #
    #   Speaker
    #

    def test_num_speakers(self):
        self.assertEqual(3, self.dataset.num_speakers)

    def test_add_speaker(self):
        spk_obj = self.dataset.add_speaker()

        self.assertIsNotNone(spk_obj.idx)
        self.assertEqual(spk_obj, self.dataset.speakers[spk_obj.idx])

    #
    #   Segmentation
    #

    def test_add_segmentation(self):
        file_path = resources.get_wav_file_path('wav_2')
        file_obj = self.dataset.add_file(file_path)

        utt_obj = self.dataset.add_utterance(file_obj.idx)

        seg_obj = self.dataset.add_segmentation(utt_obj.idx, segments='who am i')

        self.assertEqual(utt_obj.idx, seg_obj.utterance_idx)
        self.assertEqual('text', seg_obj.key)
        self.assertEqual(3, len(seg_obj.segments))

        self.assertEqual(seg_obj, self.dataset.segmentations[utt_obj.idx][seg_obj.key])

    #
    #   Div
    #

    def test_import_dataset(self):
        imp_dataset = resources.create_dataset()
        utt4 = imp_dataset.utterances['utt-4']
        utt4.idx = 'utt-4-imp'

        imp_dataset.utterances[utt4.idx] = utt4
        del imp_dataset.utterances['utt-4']

        imp_dataset.segmentations[utt4.idx] = imp_dataset.segmentations['utt-4']
        del imp_dataset.segmentations['utt-4']

        self.dataset.import_dataset(imp_dataset, copy_files=True)

        self.assertEqual(8, self.dataset.num_files)
        self.assertEqual(6, self.dataset.num_speakers)
        self.assertEqual(10, self.dataset.num_utterances)
        self.assertEqual(10, len(self.dataset.segmentations))

        self.assertEqual(1, len(os.listdir(self.dataset.path)))
        self.assertEqual(4, len(os.listdir(os.path.join(self.dataset.path, 'audio_files'))))

        self.assertIn('utt-4-imp', self.dataset.utterances)
        self.assertEqual('utt-4-imp', self.dataset.utterances['utt-4-imp'].idx)
        self.assertEqual(15, self.dataset.utterances['utt-4-imp'].start)
        self.assertEqual(25, self.dataset.utterances['utt-4-imp'].end)

        shutil.rmtree(imp_dataset.path, ignore_errors=True)
