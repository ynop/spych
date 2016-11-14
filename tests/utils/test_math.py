import unittest

from spych.utils import math


class MathUtilsTest(unittest.TestCase):
    def test_calculate_absolute_proportions(self):
        result = math.calculate_absolute_proportions(100, {'a': 0.5, 'b': 0.5})
        self.assertDictEqual({'a': 50, 'b': 50}, result)

        result = math.calculate_absolute_proportions(100, {'a': 0.6, 'b': 0.2, 'c':0.2})
        self.assertDictEqual({'a': 60, 'b': 20, 'c':20}, result)

        result = math.calculate_absolute_proportions(100, {'a': 2.0, 'b': 1.5, 'c': 1.5})
        self.assertDictEqual({'a': 40, 'b': 30, 'c': 30}, result)

        result = math.calculate_absolute_proportions(17, {'a': 0.6, 'b': 0.2, 'c':0.2})
        self.assertEquals(17, sum(result.values()))