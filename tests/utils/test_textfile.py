import os
import unittest

from spych.utils import textfile


class TextFileUtilsTest(unittest.TestCase):
    def test_read_separated_lines(self):
        file_path = os.path.join(os.path.dirname(__file__), 'multi_column_file.txt')

        expected = [
            ['a', '1', 'x'],
            ['b', '2', 'y'],
            ['c', '3', 'z']
        ]

        records = textfile.read_separated_lines(file_path, separator="\t")

        self.assertListEqual(expected, records)

    def test_read_separated_lines_with_first_key(self):
        file_path = os.path.join(os.path.dirname(__file__), 'multi_column_file.txt')

        expected = {
            'a': ['1', 'x'],
            'b': ['2', 'y'],
            'c': ['3', 'z']
        }

        records = textfile.read_separated_lines_with_first_key(file_path, separator="\t")

        self.assertDictEqual(expected, records)

    def test_read_key_value_lines(self):
        file_path = os.path.join(os.path.dirname(__file__), 'key_value_file.txt')

        expected = {
            'a': '1',
            'b': '2',
            'c': '3'
        }

        records = textfile.read_key_value_lines(file_path, separator=" ")

        self.assertDictEqual(expected, records)


if __name__ == '__main__':
    unittest.main()
