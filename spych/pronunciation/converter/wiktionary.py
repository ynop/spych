import re

from lxml import etree

from spych.pronunciation import lexicon


class WiktionaryParser(object):
    def __init__(self):
        self.lang_pattern = re.compile(r"\{\{Sprache\|(.*?)\}\}")
        self.word_types_pattern = re.compile(r"\{\{Wortart\|(.*?)(\|.*?)?\}\}")
        self.pron_pattern = re.compile(r"\{\{IPA\}\} \{\{Lautschrift\|(.*?)\}\}")
        self.langs = set()
        self.word_types = set()

        self.allowed_langs = [v.lower() for v in ['deutsch']]
        self.disallowed_word_types = [v.lower() for v in ['Abkürzung (Deutsch)',
                                                          'Abkürzung',
                                                          '?',
                                                          'Symbol'
                                                          'Suffix',
                                                          'Ortsnamengrundwort']]

    def parse_xml_dump_and_save_lexicon(self, xml_dump_path, lexicon_path):
        lex = self.parse_xml_dump(xml_dump_path)
        lex.save_at_path(lexicon_path)

    def parse_xml_dump(self, xml_dump_path):
        dictionary = lexicon.Lexicon()

        f = open(xml_dump_path, 'rb')

        for _, element in etree.iterparse(f, tag='{http://www.mediawiki.org/xml/export-0.10/}page'):
            title_element = element.find('{http://www.mediawiki.org/xml/export-0.10/}title')

            if title_element is not None:
                revision_element = element.find('{http://www.mediawiki.org/xml/export-0.10/}revision')

                if revision_element is not None:
                    text_element = revision_element.find('{http://www.mediawiki.org/xml/export-0.10/}text')

                    if text_element is not None:
                        pronunciation = self.extract_pronunciation_from_text(text_element.text)

                        if pronunciation is not None:
                            dictionary.add_entry(title_element.text, pronunciation)

            element.clear()

        print("\n\n\nLanguages:")

        for lang in self.langs:
            print(lang)

        print("\n\n\nTypes:")

        for wtype in self.word_types:
            print(wtype)

        return dictionary

    def extract_pronunciation_from_text(self, text):
        if text is None:
            return

        lang_match = self.lang_pattern.search(text)

        if lang_match:
            self.langs.add(lang_match.group(1))
            if lang_match.group(1).lower() not in self.allowed_langs:
                return
        else:
            return

        type_matches = self.word_types_pattern.findall(text)

        if len(type_matches) == 0:
            return

        for type_match in type_matches:
            splitted = type_match[0]
            self.word_types.add(splitted)

            if type_match[0].lower() in self.disallowed_word_types:
                return

        match = self.pron_pattern.search(text)

        if match:
            pronunciation = match.group(1)

            if pronunciation is not None and len(pronunciation) > 1:
                return pronunciation
