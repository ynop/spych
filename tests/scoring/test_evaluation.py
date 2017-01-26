import unittest

from spych.scoring import align
from spych.scoring import sequence
from spych.scoring import evaluation


class EvaluatorTest(unittest.TestCase):
    def setUp(self):
        self.evaluator = evaluation.Evaluator()

    def test_score(self):
        pairs = [
            (sequence.SequenceItem('sam', 0.1, 0.7), sequence.SequenceItem('sam', 0.2, 0.7)),
            (sequence.SequenceItem('crowley', 8.2, 1.5), sequence.SequenceItem('crowley', 8.1, 1.7)),
            (sequence.SequenceItem('dean', 14.2, 2.6), sequence.SequenceItem('cas', 14.4, 2.6)),
            (None, sequence.SequenceItem('crowley', 18.2, 1.3)),
            (sequence.SequenceItem('sam', 19.3, 2.8), sequence.SequenceItem('sam', 19.3, 2.8)),
            (sequence.SequenceItem('cas', 25.7, 7.4), None),
            (sequence.SequenceItem('dean', 40.2, 10.1), sequence.SequenceItem('dean', 41.3, 9.8))
        ]

        alignment = align.Alignment(None, None, pairs)

        result = self.evaluator.match(alignment)

        self.assertSetEqual(set(['dean', 'sam', 'crowley', 'cas']), set(result.labels.keys()))

        self.assertEqual(1, result.labels['dean'].correct)
        self.assertEqual(0, result.labels['dean'].insertions)
        self.assertEqual(0, result.labels['dean'].deletions)
        self.assertSetEqual(set(['cas']), set(result.labels['dean'].substitutions.keys()))
        self.assertEqual(1, result.labels['dean'].substitutions['cas'])

        self.assertEqual(2, result.labels['sam'].correct)
        self.assertEqual(0, result.labels['sam'].insertions)
        self.assertEqual(0, result.labels['sam'].deletions)
        self.assertSetEqual(set(), set(result.labels['sam'].substitutions.keys()))

        self.assertEqual(1, result.labels['crowley'].correct)
        self.assertEqual(1, result.labels['crowley'].insertions)
        self.assertEqual(0, result.labels['crowley'].deletions)
        self.assertSetEqual(set(), set(result.labels['crowley'].substitutions.keys()))

        self.assertEqual(0, result.labels['cas'].correct)
        self.assertEqual(0, result.labels['cas'].insertions)
        self.assertEqual(1, result.labels['cas'].deletions)
        self.assertSetEqual(set(), set(result.labels['cas'].substitutions.keys()))
