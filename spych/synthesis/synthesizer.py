import os
import uuid

from spych.data import dataset
from spych.utils import textfile
from spych.utils import text


class SynthesizerEffect(object):
    """
    Represents an effect used to synthesize text.
    """

    def __init__(self, name, values):
        self.name = name
        self.values = values

    def get_effect_variants(self):
        variants = []

        for settings in self.values:
            alias = None
            value = settings['value']

            prefix = ''
            suffix = ''

            if 'alias' in settings.keys() and settings['prefix'] not in [None, '']:
                alias = settings['alias']

            if 'prefix' in settings.keys() and settings['prefix'] is not None:
                prefix = settings['prefix']

            if 'suffix' in settings.keys() and settings['suffix'] is not None:
                suffix = settings['suffix']

            if type(value) == list:
                i = value[0]

                while i <= value[1]:
                    param = '{}{}{}'.format(prefix, i, suffix)

                    if alias not in [None, '']:
                        variants.append((self.name, param, '{}{}'.format(alias, i)))
                    else:
                        variants.append((self.name, param, '{}'.format(i)))

                    i += value[2]
            else:
                param = '{}{}{}'.format(prefix, value, suffix)

                if alias not in [None, '']:
                    variants.append((self.name, param, alias))
                else:
                    variants.append((self.name, param, value))

        return variants


class SynthesizerConfig(object):
    """
    Represents a config used to synthesize text.
    """

    def __init__(self, voices=[], effects={}, locale='de'):
        """
        Create a config.

        :param voices: List of voices (strings)
        :param effects: Audio effects [Name/list of settings]
        """
        self.voices = voices
        self.locale = locale
        self.effects = []

        for name, settings in effects.items():
            self.effects.append(SynthesizerEffect(name, settings))

    def generate_config_variants(self):
        for voice in self.voices:
            for effect_variant in self.get_config_variants_for_effect_with_index(0):
                name = voice
                effects = {}

                for effect in effect_variant:
                    name = '{}-{}{}'.format(name, effect[0], effect[2])
                    effects[effect[0]] = effect[1]

                name = text.remove_punctuation(name, exceptions=['-'])

                yield (name, voice, effects)

    def get_config_variants_for_effect_with_index(self, index):
        variants = []

        part_variants = self.effects[index].get_effect_variants()

        for part_variant in part_variants:
            variants.append([part_variant])

        if index + 1 < len(self.effects):
            sub_variants = self.get_config_variants_for_effect_with_index(index + 1)
            for sub_variant in sub_variants:
                variants.append(sub_variant)

                for part_variant in part_variants:
                    combined = list([part_variant])
                    combined.extend(sub_variant)
                    variants.append(combined)

        return variants


class Synthesizer(object):
    """
    Base class for any synthesizer implementation.
    """

    def __init__(self, config=None):
        """
        Create a synthesizer.

        :param config: Configuration to use.
        """
        self._config = config

        if self._config is None:
            self._config = SynthesizerConfig()

    def synthesize_text(self, text, path, voice, effects={}):
        """
        Synthesize the given text and save it at path.

        :param text: Text
        :param path: Path
        """
        pass

    def synthesize_sentences(self, sentences, destination_folder, voice, effects={}):
        """
        Synthesize all sentences and save the files (ID as filename) in the given folder.

        sentences : {ID : SENTENCE}

        :param sentences: Dict with id/sentence pairs.
        :param destination_folder: Path to store the synthesized speech.
        """

        for sentence_id, sentence in sentences.items():
            file_name = sentence_id
            file_path = os.path.join(destination_folder, file_name)

            self.synthesize_text(sentence, file_path, voice, effects)

    def synthesize_sentence_corpus_and_create_dataset(self, corpus_path, destination_folder, corpus_clean_path=None):
        """
        Synthesizes all sentences from corpus and create dataset from it.

        corpus format (tab separated): ID   SENTENCE

        :param corpus_path: Path to corpus
        :param destination_folder: Path to save the dataset
        :param corpus_clean_path: Cleaned sentences if available (same format)
        :return: dataset
        """

        data = dataset.Dataset(dataset_folder=destination_folder)
        data.save()

        sentences = textfile.read_key_value_lines(corpus_path, separator='\t')
        sentences_cleaned = {}

        speaker_id = str(uuid.uuid1())

        wavs = {}
        utterances = {}
        transcriptions = {}
        transcriptions_raw = {}
        utt2spk = {}
        speaker_info = {

        }

        if corpus_clean_path is not None:
            sentences_cleaned = textfile.read_key_value_lines(corpus_clean_path, separator='\t')

        for sentence_id, sentence in sentences.items():
            transcription_raw = sentence

            if sentence_id in sentences_cleaned.keys():
                transcription = sentences_cleaned[sentence_id]
            else:
                transcription = text.remove_punctuation(sentence)

            for config_variant in self._config.generate_config_variants():
                speaker_id = config_variant[0]
                voice = config_variant[1]
                effects = config_variant[2]

                wav_id = '{}_{}'.format(speaker_id, sentence_id)
                utt_id = wav_id
                file_name = '{}.wav'.format(wav_id)
                file_path = os.path.join(data.path, file_name)
                self.synthesize_text(sentence, file_path, voice, effects)

                wavs[wav_id] = file_path
                utterances[utt_id] = [wav_id]
                transcriptions_raw[utt_id] = transcription_raw
                transcriptions[utt_id] = transcription
                utt2spk[utt_id] = speaker_id
                speaker_info[speaker_id] = {
                    dataset.SPEAKER_INFO_SYNTHESIZED: True,
                    dataset.SPEAKER_INFO_SYNTHESIZER_TOOL: "marytts",
                    dataset.SPEAKER_INFO_SYNTHESIZER_EFFECTS: effects,
                    dataset.SPEAKER_INFO_SYNTHESIZER_VOICE: voice,
                    dataset.SPEAKER_INFO_GENDER : "m"
                }

        wav_id_mapping = data.import_wavs(wavs, copy_files=False)
        utt_id_mapping = data.add_utterances(utterances, wav_id_mapping=wav_id_mapping)
        speaker_id_mapping = data.add_speaker_info(speaker_info)
        data.set_transcriptions(transcriptions, utt_id_mapping=utt_id_mapping)
        data.set_transcriptions_raw(transcriptions_raw, utt_id_mapping=utt_id_mapping)
        data.set_utt2spk(utt2spk, utt_id_mapping=utt_id_mapping, speaker_id_mapping=speaker_id_mapping)

        data.save()

        return data
