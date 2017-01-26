import unittest

from spych.scoring import align
from spych.scoring import sequence


class TimeBasedAlignerTest(unittest.TestCase):
    def setUp(self):
        self.ref_seq = sequence.Sequence.from_tuples([
            ('sam', 0.1, 0.7),
            ('crowley', 8.2, 1.5),
            ('dean', 14.2, 2.6),
            ('sam', 19.3, 2.8),
            ('cas', 25.7, 7.4),
            ('dean', 40.2, 10.1)
        ])

        self.hyp_seq = sequence.Sequence.from_tuples([
            ('sam', 0.2, 0.7),
            ('crowley', 8.1, 1.7),
            ('cas', 14.4, 2.6),
            ('crowley', 18.2, 1.3),
            ('sam', 19.3, 2.8),
            ('dean', 41.3, 9.8)
        ])

        self.aligner = align.TimeBasedAligner()

    def test_align(self):
        result = self.aligner.align(self.ref_seq, self.hyp_seq)

        expected_pairs = [
            (self.ref_seq.items[0], self.hyp_seq.items[0]),
            (self.ref_seq.items[1], self.hyp_seq.items[1]),
            (self.ref_seq.items[2], self.hyp_seq.items[2]),
            (None, self.hyp_seq.items[3]),
            (self.ref_seq.items[3], self.hyp_seq.items[4]),
            (self.ref_seq.items[4], None),
            (self.ref_seq.items[5], self.hyp_seq.items[5])
        ]

        self.assertEqual(self.ref_seq, result.reference_sequence)
        self.assertEqual(self.hyp_seq, result.hypothesis_sequence)
        self.assertEqual(len(expected_pairs), len(result.pairs))

        for pair in expected_pairs:
            self.assertTrue(pair in result.pairs)
