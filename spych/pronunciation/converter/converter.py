class LexiconConverter(object):
    """
    Generate pronunciation for words or creates full lexicon from a specific source.
    """

    def convert_word_to_phones(self, word):
        """
        Creates pronunciation for the given word.

        :param word: Word
        :return: List of Pronunciations (space separated phones)
        """
        raise NotImplementedError("convert_word_to_phones not available.")

    def convert_words_to_phones(self, words):
        """
        Creates pronunciations for all given words.

        :param words: List of words.
        :return: Dict [Word/List of Pronunciations (space separated phones)]
        """
        raise NotImplementedError("convert_words_to_phones not available.")

    def create_full_lexicon(self):
        """
        Create a lexicon with all available words.

        :return: Lexicon
        """
        raise NotImplementedError("create_full_lexicon not available.")
