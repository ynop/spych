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

    def __init__(self, entries=None, case_sensitive=False):
        """
        Create Lexicon.

        :param entries: Entries
        :param case_sensitive: if False all will be converted to lower case.
        """
        self.case_sensitive=case_sensitive
        self.entries = entries or collections.defaultdict(set)

    def add_entry(self, word, pronunciation):
        """
        Adds the pronunciation for the given word.

        :param word: Word
        :param pronunciation: Pronunciation (space separated phones) or list of pronunciations
        """

        if type(pronunciation) == list:
            self.entries[word].update(pronunciation)
        else:
            self.entries[word].add(pronunciation)

    def add_entries(self, entries):
        """
        Update the lexicon with the given entries.

        :param entries: Entries to add
        """
        for word, pronunciations in entries.items():
            self.add_entry(word, pronunciations)

    def remove_entry(self, word):
        """
        Removes all pronunciations for the given word.

        :param word: Word
        """
        del self.entries[word]

    def get_number_of_entries(self, count_all=True):
        """
        Get number of entries.

        :param count_all: If True it also count multiple pronunciations per word.
        :return: Count
        """
        if count_all:
            count = 0
            for value, pronunciations in self.entries.items():
                count += len(pronunciations)

            return count
        else:
            return len(self.entries)

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
