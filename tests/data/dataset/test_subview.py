import unittest

from spych.data.dataset import subview

from tests.data import resources


class DatasetTest(unittest.TestCase):
    def setUp(self):
        self.testset = resources.create_dataset()

    def test_filter_utterances(self):
        filtered_utts = set(['utt-2', 'utt-4'])

        view = subview.Subview(filtered_utterances=filtered_utts, dataset=self.testset)

        self.assertSetEqual(set(['wav_2', 'wav_3']), set(view.files.keys()))
        self.assertSetEqual(filtered_utts, set(view.utterances.keys()))
        self.assertSetEqual(set([self.testset.utterances['utt-2'].speaker_idx, 'spk-2']), set(view.speakers.keys()))

    def test_filter_speakers(self):
        filtered_spks = set(['spk-2'])

        view = subview.Subview(filtered_speakers=filtered_spks, dataset=self.testset)

        self.assertSetEqual(set(['wav_3']), set(view.files.keys()))
        self.assertSetEqual(set(['utt-3', 'utt-4']), set(view.utterances.keys()))
        self.assertSetEqual(filtered_spks, set(view.speakers.keys()))