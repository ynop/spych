import unittest

from spych.pronunciation.converter import wiktionary


class WiktionaryParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = wiktionary.WiktionaryParser()

    def test_extract_pronunciation_from_text(self):
        result = self.parser.extract_pronunciation_from_text(
            '{{Aussprache}} \n:{{IPA}} {{Lautschrift|haˈloː}} \n:{{Hörbeispiele}} {{Audio|De-Hallo.ogg}}'
        )

        self.assertEqual('haˈloː', result)
