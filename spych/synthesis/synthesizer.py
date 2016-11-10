import os
import uuid

from spych.data import dataset
from spych.utils import textfile
from spych.utils import text


class SynthesizerConfig(object):
    """
    Represents a config used to synthesize text.
    """

    def __init__(self, locale='de', voice=None, effects={}):
        """
        Create a config.

        :param locale: Language/Locale
        :param voice: Voice [string] (depends on the synthesizer)
        :param effects: Audio effects [Name/Value dict] (depends on synthesizer)
        """
        self.locale = locale
        self.voice = voice
        self.effects = dict(effects)

    @classmethod
    def german(cls):
        """
        Config for german synthesizer with default voice and no effects.

        :return: Config
        """
        return cls(locale='de')

    @classmethod
    def english_us(cls):
        """
        Config for US english synthesizer with default voice and no effects.
        :return: Config
        """
        return cls(locale='en_US')


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

    def synthesize_text(self, text, path):
        """
        Synthesize the given text and save it at path.

        :param text: Text
        :param path: Path
        """
        pass

    def synthesize_sentences(self, sentences, destination_folder):
        """
        Synthesize all sentences and save the files (ID as filename) in the given folder.

        sentences : {ID : SENTENCE}

        :param sentences: Dict with id/sentence pairs.
        :param destination_folder: Path to store the synthesized speech.
        """

        for sentence_id, sentence in sentences.items():
            file_name = sentence_id
            file_path = os.path.join(destination_folder, file_name)

            self.synthesize_text(sentence, file_path)

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

        if corpus_clean_path is not None:
            sentences_cleaned = textfile.read_key_value_lines(corpus_clean_path, separator='\t')

        for sentence_id, sentence in sentences.items():
            wav_id = sentence_id
            utt_id = '{}_{}'.format(speaker_id, wav_id)
            transcription_raw = sentence

            if sentence_id in sentences_cleaned.keys():
                transcription = sentences_cleaned[sentence_id]
            else:
                transcription = text.remove_punctuation(sentence)

            file_name = '{}.wav'.format(wav_id)
            file_path = os.path.join(data.path, file_name)
            self.synthesize_text(sentence, file_path)

            wavs[wav_id] = file_path
            utterances[utt_id] = [wav_id]
            transcriptions_raw[utt_id] = transcription_raw
            transcriptions[utt_id] = transcription
            utt2spk[utt_id] = speaker_id

        wav_id_mapping = data.import_wavs(wavs, copy_files=False)
        utt_id_mapping = data.add_utterances(utterances, wav_id_mapping=wav_id_mapping)
        data.set_transcriptions(transcriptions, utt_id_mapping=utt_id_mapping)
        data.set_transcriptions_raw(transcriptions_raw, utt_id_mapping=utt_id_mapping)
        data.set_utt2spk(utt2spk, utt_id_mapping=utt_id_mapping)

        data.save()

        return data

