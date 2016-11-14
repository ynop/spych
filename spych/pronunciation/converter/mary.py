from spych.pronunciation.converter import converter
from spych.tools import marytts


class MaryLexiconConverter(converter.LexiconConverter):
    """
    Implements a lexicon convert using MaryTTS. MaryTTS server needs to be running.
    """

    def __init__(self, host=marytts.MARY_DEFAULT_HOST, port=marytts.MARY_DEFAULT_PORT):
        """
        Create Converter. Needs a running maryTTS server.

        :param host: Host where maryTTS is running.
        :param port: Port where maryTTS is listening.
        """
        converter.LexiconConverter.__init__(self)
        self.host = host
        self.port = port

        self.maryClient = marytts.MaryClient(host=host, port=port)

    def convert_word_to_phones(self, word, locale='en_US'):
        pronunciation = self.maryClient.phonemes(word, locale=locale)

        if pronunciation is not None:
            return [pronunciation]
