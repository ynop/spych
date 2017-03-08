import unittest

from spych.data.dataset import iteration

from tests.data import resources


class BatchGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.test_set_a = resources.create_dataset()
        self.test_set_b = resources.create_dataset()

        # Add two utts so 5 equal utts in both sets
        self.test_set_a.add_utterance('wav_2', utterance_idx='utt_na')
        self.test_set_b.add_utterance('wav_2', utterance_idx='utt_na')

        self.test_set_a.add_utterance('wav_3', utterance_idx='utt_nb')
        self.test_set_b.add_utterance('wav_3', utterance_idx='utt_nb')

        # Add one different to one set
        self.test_set_b.add_utterance('wav_4', utterance_idx='utt_diff')

    def test_generate_utterance_batches(self):
        generator = iteration.BatchGenerator(self.test_set_a)

        batches = [x for x in generator.generate_utterance_batches(2)]

        self.assertEqual(4, len(batches))

        self.assertEqual(2, len(batches[0]))
        self.assertEqual(2, len(batches[1]))
        self.assertEqual(2, len(batches[2]))
        self.assertEqual(1, len(batches[3]))

    def test_generate_utterance_batches_two_sets(self):
        generator = iteration.BatchGenerator([self.test_set_a, self.test_set_b])

        batches = [x for x in generator.generate_utterance_batches(2)]

        self.assertEqual(3, len(batches))

        self.assertEqual(2, len(batches[0]))
        self.assertEqual(2, len(batches[1]))
        self.assertEqual(1, len(batches[2]))

    def test_generate_utterance_batches_randomly(self):
        generator = iteration.BatchGenerator([self.test_set_a, self.test_set_b])

        first_run = [x for x in generator.generate_utterance_batches(2)]
        second_run = [x for x in generator.generate_utterance_batches(2)]
        third_run = [x for x in generator.generate_utterance_batches(2)]

        self.assertFalse(first_run == second_run and first_run == third_run)
