import unittest

import numpy as np

from spych.utils import array


class MathUtilsTest(unittest.TestCase):
    def setUp(self):
        self.input_features = np.array([
            [1, 2],
            [3, 4],
            [5, 6],
            [7, 8],
            [9, 10],
            [11, 12],
            [13, 14],
            [15, 16],
        ])

        self.output_features = np.array([
            [1, 2, 1, 2, 1, 2, 3, 4, 5, 6],
            [1, 2, 1, 2, 3, 4, 5, 6, 7, 8],
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            [5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
            [7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
            [9, 10, 11, 12, 13, 14, 15, 16, 15, 16],
            [11, 12, 13, 14, 15, 16, 15, 16, 15, 16]
        ])

        self.output_features_step_two = np.array([
            [1, 2, 1, 2, 1, 2, 3, 4, 5, 6],
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
            [9, 10, 11, 12, 13, 14, 15, 16, 15, 16]
        ])

        self.input_features_odd = np.array([
            [1, 2],
            [3, 4],
            [5, 6],
            [7, 8],
            [9, 10],
            [11, 12],
            [13, 14],
            [15, 16],
            [17, 18],
        ])

        self.output_features_odd = np.array([
            [1, 2, 1, 2, 1, 2, 3, 4, 5, 6],
            [1, 2, 1, 2, 3, 4, 5, 6, 7, 8],
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            [5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
            [7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
            [9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            [11, 12, 13, 14, 15, 16, 17, 18, 17, 18],
            [13, 14, 15, 16, 17, 18, 17, 18, 17, 18]
        ])

        self.output_features_odd_step_two = np.array([
            [1, 2, 1, 2, 1, 2, 3, 4, 5, 6],
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
            [9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            [13, 14, 15, 16, 17, 18, 17, 18, 17, 18]
        ])

    def test_splice_feature_no_splice(self):
        result = array.splice_features(self.input_features, splice_size=0, splice_step=1, repeat_border_frames=True)
        np.testing.assert_array_equal(self.input_features, result)

    def test_splice_features_step_one(self):
        result = array.splice_features(self.input_features, splice_size=2, splice_step=1, repeat_border_frames=True)
        np.testing.assert_array_equal(self.output_features, result)

    def test_splice_features_odd_step_one(self):
        result = array.splice_features(self.input_features_odd, splice_size=2, splice_step=1, repeat_border_frames=True)
        np.testing.assert_array_equal(self.output_features_odd, result)

    def test_splice_features_step_two(self):
        result = array.splice_features(self.input_features, splice_size=2, splice_step=2, repeat_border_frames=True)
        np.testing.assert_array_equal(self.output_features_step_two, result)

    def test_splice_features_odd_step_two(self):
        result = array.splice_features(self.input_features_odd, splice_size=2, splice_step=2, repeat_border_frames=True)
        np.testing.assert_array_equal(self.output_features_odd_step_two, result)

    def test_unsplice_feature_no_splice(self):
        result = array.unsplice_features(self.input_features, splice_size=0, splice_step=1)
        np.testing.assert_array_equal(self.input_features, result)

    def test_unsplice_features_step_one(self):
        result = array.unsplice_features(self.output_features, splice_size=2, splice_step=1)
        np.testing.assert_array_equal(self.input_features, result)

    def test_unsplice_features_odd_step_one(self):
        result = array.unsplice_features(self.output_features_odd, splice_size=2, splice_step=1)
        np.testing.assert_array_equal(self.input_features_odd, result)

    def test_unsplice_features_step_two(self):
        result = array.unsplice_features(self.output_features_step_two, splice_size=2, splice_step=2)
        np.testing.assert_array_equal(self.input_features, result)

    def test_unsplice_features_odd_step_two(self):
        output = self.input_features_odd.copy()
        output = np.append(output, [[17, 18]], 0)

        result = array.unsplice_features(self.output_features_odd_step_two, splice_size=2, splice_step=2)
        np.testing.assert_array_equal(output, result)
