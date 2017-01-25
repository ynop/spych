import unittest

from spych.scoring import sequence


class SequenceTest(unittest.TestCase):

    def setUp(self):
        self.items = [
            sequence.SequenceItem('sam', 0.1, 0.7),
            sequence.SequenceItem('dean', 14.2, 2.6),
            sequence.SequenceItem('crowly', 8.2, 1.5),
            sequence.SequenceItem('cas', 25.7, 7.4),
            sequence.SequenceItem('dean', 40.2, 10.1),
            sequence.SequenceItem('sam', 19.3, 2.8),
        ]

        self.seq = sequence.Sequence(items=self.items)

    def test_items_in_interval_with_range_within_item(self):
        # |--(---)--|
        self.assertListEqual([(3, self.items[3])], self.seq.items_in_interval(26.1, 30.2))

    def test_items_in_interval_with_range_around_item(self):
        # (--|--|--)
        self.assertListEqual([(3, self.items[3])], self.seq.items_in_interval(25.0, 33.9))

    def test_items_in_interval_with_range_around_start_of_item(self):
        # (--|--)--|
        self.assertListEqual([(3, self.items[3])], self.seq.items_in_interval(24.2, 26.7))

    def test_items_in_interval_with_range_around_end_of_item(self):
        # |--(--|--)
        self.assertListEqual([(3, self.items[3])], self.seq.items_in_interval(33.0, 33.2))

    def test_items_in_interval_with_range_before_item(self):
        # (--) |----|
        self.assertListEqual([], self.seq.items_in_interval(24.2, 25.69))

    def test_items_in_interval_with_range_after_item(self):
        # |----| (--)
        self.assertListEqual([], self.seq.items_in_interval(33.5, 36.1))

    def test_items_in_interval_with_invalid_range(self):
        with self.assertRaises(ValueError):
            self.seq.items_in_interval(14.0, 13.8)