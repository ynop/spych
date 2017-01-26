import unittest

from spych.scoring import result


class LabelScoreTest(unittest.TestCase):
    def setUp(self):
        self.label_score = result.LabelScore()
        self.label_score.correct = 4
        self.label_score.insertions = 1
        self.label_score.deletions = 0
        self.label_score.substitutions = {
            'dean': 1,
            'crowley': 2
        }

    def test_total(self):
        self.assertEqual(7, self.label_score.total)


class ScoreTest(unittest.TestCase):
    def setUp(self):
        self.result = result.Score()

        label = result.LabelScore()
        label.correct = 4
        label.insertions = 1
        label.deletions = 0
        label.substitutions = {
            'dean': 1
        }
        self.result.labels['sam'] = label

        label = result.LabelScore()
        label.correct = 2
        label.insertions = 0
        label.deletions = 1
        label.substitutions = {
        }
        self.result.labels['dean'] = label

        label = result.LabelScore()
        label.correct = 5
        label.insertions = 0
        label.deletions = 0
        label.substitutions = {
            'cas': 1,
            'dean': 2
        }
        self.result.labels['crowley'] = label

        label = result.LabelScore()
        label.correct = 3
        label.insertions = 2
        label.deletions = 0
        label.substitutions = {
            'dean': 1
        }
        self.result.labels['cas'] = label

    def test_total(self):
        self.assertEqual(20, self.result.num_total)

    def test_correct(self):
        self.assertEqual(14, self.result.num_correct)

    def test_deletions(self):
        self.assertEqual(1, self.result.num_deletions)

    def test_insertions(self):
        self.assertEqual(3, self.result.num_insertions)

    def test_num_substitutions(self):
        self.assertEqual(5, self.result.num_substitutions)

    def test_error_rate(self):
        self.assertEqual(9 / 20, self.result.error_rate)

    def test_accuracy(self):
        self.assertEqual(14 / 20, self.result.accuracy)


class ScoreAggregationTest(unittest.TestCase):
    def setUp(self):
        self.aggregation = result.ScoreAggregation()

        sc = result.Score()

        label = result.LabelScore()
        label.correct = 4
        label.insertions = 1
        label.deletions = 0
        label.substitutions = {
            'dean': 1
        }
        sc.labels['sam'] = label

        label = result.LabelScore()
        label.correct = 2
        label.insertions = 0
        label.deletions = 1
        label.substitutions = {
        }
        sc.labels['dean'] = label
        self.aggregation.scores['utt1'] = sc

        sc = result.Score()

        label = result.LabelScore()
        label.correct = 5
        label.insertions = 0
        label.deletions = 0
        label.substitutions = {
            'cas': 1,
            'dean': 2
        }
        sc.labels['crowley'] = label

        label = result.LabelScore()
        label.correct = 2
        label.insertions = 0
        label.deletions = 1
        label.substitutions = {
            'dean': 2
        }
        sc.labels['sam'] = label

        label = result.LabelScore()
        label.correct = 3
        label.insertions = 2
        label.deletions = 0
        label.substitutions = {
            'dean': 1
        }
        sc.labels['cas'] = label
        self.aggregation.scores['utt2'] = sc

    def test_total(self):
        self.assertEqual(25, self.aggregation.num_total)

    def test_correct(self):
        self.assertEqual(16, self.aggregation.num_correct)

    def test_deletions(self):
        self.assertEqual(2, self.aggregation.num_deletions)

    def test_insertions(self):
        self.assertEqual(3, self.aggregation.num_insertions)

    def test_num_substitutions(self):
        self.assertEqual(7, self.aggregation.num_substitutions)

    def test_error_rate(self):
        self.assertEqual(12 / 25, self.aggregation.error_rate)

    def test_accuracy(self):
        self.assertEqual(16 / 25, self.aggregation.accuracy)

    def test_aggregated_label_stats(self):
        result = self.aggregation.aggregated_label_stats

        self.assertEqual(set(['sam', 'dean', 'crowley', 'cas']), set(list(result.labels.keys())))

        self.assertEqual(2, result.labels['dean'].correct)
        self.assertEqual(0, result.labels['dean'].insertions)
        self.assertEqual(1, result.labels['dean'].deletions)
        self.assertSetEqual(set(), set(result.labels['dean'].substitutions.keys()))

        self.assertEqual(6, result.labels['sam'].correct)
        self.assertEqual(1, result.labels['sam'].insertions)
        self.assertEqual(1, result.labels['sam'].deletions)
        self.assertSetEqual(set(['dean']), set(result.labels['sam'].substitutions.keys()))
        self.assertEqual(3, result.labels['sam'].substitutions['dean'])

        self.assertEqual(5, result.labels['crowley'].correct)
        self.assertEqual(0, result.labels['crowley'].insertions)
        self.assertEqual(0, result.labels['crowley'].deletions)
        self.assertSetEqual(set(['cas', 'dean']), set(result.labels['crowley'].substitutions.keys()))
        self.assertEqual(2, result.labels['crowley'].substitutions['dean'])
        self.assertEqual(1, result.labels['crowley'].substitutions['cas'])

        self.assertEqual(3, result.labels['cas'].correct)
        self.assertEqual(2, result.labels['cas'].insertions)
        self.assertEqual(0, result.labels['cas'].deletions)
        self.assertSetEqual(set(['dean']), set(result.labels['cas'].substitutions.keys()))
        self.assertEqual(1, result.labels['cas'].substitutions['dean'])
