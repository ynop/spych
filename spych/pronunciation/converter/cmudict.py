import re

try:
    import urllib.request as request
except ImportError:
    import urllib2 as request

from spych.pronunciation.converter import converter

CMU_DICT_URL = "http://www.speech.cs.cmu.edu/cgi-bin/cmudict?in="


class CMUDictLexiconConverter(converter.LexiconConverter):
    """
    Implements a lexicon converter using CMU Dictionary.
    """

    def __init__(self):
        """
        Create Converter.
        """
        converter.LexiconConverter.__init__(self)

    def convert_word_to_phones(self, word, locale='en_US'):
        phoneme_pattern = re.compile(r'<tt>' + str(word).upper() + '</tt>(.*?)<tt>(.*?)\.</tt>')
        response = request.urlopen('{}{}'.format(CMU_DICT_URL, str(word)))
        source = response.read().decode('utf-8')
        m = phoneme_pattern.search(source)

        if m:
            pronunciation = m.group(2)
            pronunciation = str(pronunciation).strip()

            return [pronunciation]
