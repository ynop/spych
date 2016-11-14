import httplib2
from urllib import parse
from collections import OrderedDict

from bs4 import BeautifulSoup

MARY_DEFAULT_HOST = 'localhost'
MARY_DEFAULT_PORT = '59125'

STRESS_SYMBOLS = ["'", '"', 'q']
UNNEEDED_SYMBOLS = ['?', '-']


class MaryClient:
    def __init__(self, host=MARY_DEFAULT_HOST, port=MARY_DEFAULT_PORT):
        self.host = host
        self.port = port

    def synthesize(self, text, output_file, voice=None, locale='en_US', effects={}):
        resp, content = self.execute_query(text, 'TEXT', 'AUDIO', voice, locale=locale, effects=effects)

        if resp["content-type"] == "audio/x-wav":
            # Write the wav file
            f = open(output_file, "wb")
            f.write(content)
            f.close()
        else:
            raise Exception(content)

    def phonemes(self, text, locale='en_US'):
        resp, content = self.execute_query(text, 'TEXT', 'PHONEMES', locale=locale)
        text = content.decode()

        words = parse_phonemes_from_response(text)
        phoneme_parts = []

        for phoneme_part in words.values():
            cleaned_phonemes = remove_unneeded_symbols(phoneme_part)
            cleaned_phonemes = remove_space_after_stress_symbols(cleaned_phonemes)
            phoneme_parts.append(cleaned_phonemes)

        return ' '.join(phoneme_parts)

    def execute_query(self, input_text, input_type, output_type, voice=None, audio='WAVE', locale='en_US', effects={}):
        query_hash = {
            "INPUT_TEXT": input_text,
            "INPUT_TYPE": input_type,
            "LOCALE": locale,
            "OUTPUT_TYPE": output_type
        }

        if output_type == 'AUDIO':
            query_hash["AUDIO"] = audio

        if voice is not None:
            query_hash["VOICE"] = voice

        for key, value in effects.items():
            query_hash['effect_{}_selected'.format(key)] = 'on'
            query_hash['effect_{}_parameters'.format(key)] = value

        query = parse.urlencode(query_hash)
        http = httplib2.Http()
        return http.request("http://%s:%s/process?" % (self.host, self.port), "POST", query)


def parse_phonemes_from_response(response_content):
    soup = BeautifulSoup(response_content, "lxml")

    raw_tokens = OrderedDict()

    for token in soup.find_all('t'):
        raw_tokens[str(token.string).strip()] = token.attrs

    phonemes = OrderedDict()

    for token, attributes in raw_tokens.items():
        if 'ph' in attributes:
            phonemes[token] = attributes['ph']

    return phonemes


def remove_unneeded_symbols(phonemes):
    for symbol in UNNEEDED_SYMBOLS:
        phonemes = phonemes.replace(symbol, '')

    return phonemes


def remove_space_after_stress_symbols(phonemes):
    for symbol in STRESS_SYMBOLS:
        phonemes = phonemes.replace(symbol + ' ', symbol)

    return phonemes
