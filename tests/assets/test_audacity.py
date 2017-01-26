import os
import unittest

from spych.assets import audacity


class AudacityTest(unittest.TestCase):
    def test_read_label_file(self):
        file_path = os.path.join(os.path.dirname(__file__), 'basic.txt')

        expected = [
            [3.1, 4.7, 'jingle1'],
            [15.5, 17.2, 'jingle2'],
            [22.3, 23.4, 'jingle2'],
            [25.8, 27.3, 'jingle1'],
            [35.0, 36.1, 'jingle3']
        ]

        records = audacity.read_label_file(file_path)

        self.assertListEqual(expected, records)
