import collections

from spych.utils import textfile


class Lexicon(object):
    """
    Pronunciation Lexicon

    Entries: dict(string, set)

    {
        'WORD' : ['PHONEMES 1', 'PHONEMES 2'],
        'WORD 2 ' : ['AA I', 'AA Y'],
        ...
    }

    """

    def __init__(self, entries=None):
        self.entries = entries or collections.defaultdict(set)

    def get_all_words(self):
        """
        Returns a set of all words occuring in the lexicon.

        :return: Set
        """
        return set(self.entries.keys())

    def get_all_phones(self):
        """
        Get a set of all phones that appear in the lexicon.

        :return: Set of phones
        """
        all_phones = set()

        for word, pronunciations in self.entries.items():
            for pronunciation in pronunciations:
                phones = pronunciation.strip().split(" ")
                all_phones.update(phones)

        return all_phones

    def add_entries(self, entries):
        """
        Adds entries to the lexicon.

        :param entries: dict word/set
        :return:
        """
        for word, pronunciations in entries.items():
            self.entries[word].update(pronunciations)

    def import_lexicon(self, lexicon):
        """
        Import entries from another lexicon.

        :param lexicon: Lexicon to import
        :return:
        """
        self.add_entries(lexicon.entries)

    #
    #   READ / WRITE
    #

    def save_at_path(self, path, separator=' ', index_multi_pronunciations=False):
        """
        Saves the lexicon at the given path.

        :param path: Path to save lexicon file to.
        :param separator: Seperator between word and pronunciation.
        :param index_multi_pronunciations: Adds indexes (  ALPHA(0) ALPHA(1) ) if there are multiple pronunciations for one word.
        :return:
        """
        f = open(path, 'w')

        for word in sorted(self.entries.keys()):
            for index, phones in enumerate(self.entries[word]):
                if index > 0 and index_multi_pronunciations:
                    f.write('{}({}){}{}\n'.format(word, index, separator, phones))
                else:
                    f.write('{}{}{}\n'.format(word, separator, phones))

        f.close()

    @classmethod
    def load_from_file(cls, path, separator=' ', index_multi_pronunciations=False, lower_case=True):
        """
        Load lexicon from file.

        :param path: Path to read lexicon file from.
        :param separator: Separator that is used between word and pronunciation.
        :param index_multi_pronunciations: If multiple pronunciations are indexed (  ALPHA(0) ALPHA(1) ).
        :param lower_case: if True read
        :return:
        """
        gen = textfile.read_separated_lines_generator(path, separator=separator, max_columns=2)

        entries = collections.defaultdict(set)

        for record in gen:
            if len(record) == 2:
                word = record[0]

                if lower_case:
                    word = word.lower()

                pronunciation = record[1]

                if index_multi_pronunciations:
                    word = str(word).strip().split("(")[0]

                entries[word].add(pronunciation)

        return cls(entries)
