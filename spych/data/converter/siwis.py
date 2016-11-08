import os

from spych.data import dataset
from spych.utils import textfile
from spych.utils import text


class SiwisConverter(object):
    """
    Creates database from siwis corpus for a given language.
    Can be downloaded at http://www.unige.ch/lettres/linguistique/research/current-projects/latl/siwis/.
    """

    def __init__(self, target_folder, source_folder):
        self.target_folder = target_folder
        self.source_folder = source_folder

        self.dataset = None

    def get_dataset(self, lang='DE'):
        self.dataset = dataset.Dataset(dataset_folder=self.target_folder)
        self.dataset.save()

        self.create_dataset(lang)
        self.dataset.save()

        return self.dataset

    def create_dataset(self, lang='DE'):
        wav_folder = os.path.join(self.source_folder, 'wav', lang)
        text_folder = os.path.join(self.source_folder, 'txt', lang)

        genders = None
        gender_file = os.path.join(self.source_folder, 'genders.txt')

        if os.path.exists(gender_file):
            genders = textfile.read_key_value_lines(gender_file)

        for speaker in os.listdir(wav_folder):
            speaker_wav_folder = os.path.join(wav_folder, speaker)
            speaker_txt_folder = os.path.join(text_folder, speaker)

            if os.path.isdir(speaker_wav_folder) and os.path.isdir(speaker_txt_folder):
                gender = None

                if genders is not None:
                    gender = genders[speaker]

                self.add_speaker(speaker_txt_folder, speaker_wav_folder, speaker, gender)

    def add_speaker(self, txt_folder, wav_folder, speaker, gender=None):
        wavs = {}
        segments = {}
        transcriptions = {}
        transcriptions_raw = {}
        utt2spk = {}

        for file in os.listdir(wav_folder):
            wav_path = os.path.join(wav_folder, file)
            basename, __ = os.path.splitext(file)
            txt_path = os.path.join(txt_folder, basename + '.txt')

            wav_id = basename
            utt_id = '{}_{}'.format(speaker, wav_id)

            try:
                f = open(txt_path, 'r')
                transcription = f.read().strip()
                f.close()
            except UnicodeDecodeError:
                f = open(txt_path, 'r', encoding='utf-16')
                transcription = f.read().strip()
                f.close()
            finally:
                f.close()

            if transcription is None:
                print("Failed to get transcription for {}!!!".format(file))
            else:
                transcription_raw = transcription
                transcription = text.remove_punctuation(transcription)
                transcription = transcription.upper()
                transcriptions[utt_id] = transcription
                transcription_raw[utt_id] = transcription_raw

            wavs[wav_id] = wav_path
            segments[utt_id] = [wav_id]
            utt2spk[utt_id] = speaker

        wav_id_mapping = self.dataset.import_wavs(wavs, copy_files=True)
        utt_id_mapping = self.dataset.add_utterances(segments, wav_id_mapping=wav_id_mapping)
        speaker_id_mapping = self.dataset.set_spk2gender({speaker: gender})
        self.dataset.set_transcriptions(transcriptions, utt_id_mapping=utt_id_mapping)
        self.dataset.set_transcriptions_raw(transcriptions_raw, utt_id_mapping=utt_id_mapping)
        self.dataset.set_utt2spk(utt2spk, utt_id_mapping=utt_id_mapping, speaker_id_mapping=speaker_id_mapping)
