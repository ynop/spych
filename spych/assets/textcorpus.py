from spych.utils import textfile


def get_corpus_words_missing_in_lexicon(corpus_file, lexicon, lower_case=True):
    """
    Get list of words occurring in the sentence corpus but aren't in the given lexicon.
    corpus_file has sentences \n separated.

    :param corpus_file: Path to sentence corpus file
    :param lexicon: Lexicon
    :param lower_case: Lower case compare
    :return: Set of words
    """

    lexicon_words = lexicon.get_all_words()
    missing_words = set()

    for split_sentence in textfile.read_separated_lines_generator(corpus_file, separator=' '):
        for word in split_sentence:
            cleaned_word = word

            if lower_case:
                cleaned_word = cleaned_word.lower()

            if cleaned_word not in lexicon_words:
                missing_words.add(word)

    return missing_words
