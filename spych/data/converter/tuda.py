import os

from bs4 import BeautifulSoup

from spych.data import dataset


class TudaConverter(object):
    """
    Creates database from TU Darmstadt distant speech data corpus.
    Can be downloaded at https://www.lt.informatik.tu-darmstadt.de/de/data/open-source-acoustic-models-for-german-distant-speech-recognition/.
    """

    def __init__(self, target_folder, source_folder):
        self.target_folder = target_folder
        self.source_folder = source_folder

        self.dataset = None

    def get_dataset(self):
        self.dataset = dataset.Dataset(dataset_folder=self.target_folder)
        self.dataset.save()

        self.create_dataset()
        self.dataset.save()

        return self.dataset

    def create_dataset(self):
        for part in ['train', 'dev', 'test']:
            source_path = os.path.join(self.source_folder, part)

            self.add_folder(source_path)

    def add_folder(self, source_path):
        wavs = {}
        segments = {}
        transcriptions = {}
        speakers = {}
        genders = {}

        for file in os.listdir(source_path):
            if file.endswith('.xml'):
                full_path = os.path.join(source_path, file)
                xml_file = open(full_path, 'r')
                soup = BeautifulSoup(xml_file, "xml")
                xml_id, __ = os.path.splitext(file)
                transcription = soup.recording.cleaned_sentence
                gender = soup.recording.gender.string
                speakerid = soup.recording.speaker_id.string

                for mic in ['Kinect-Beam', 'Kinect-RAW', 'Realtek', 'Samson']:
                    wav_id = '{}_{}'.format(xml_id, mic)
                    utt_id = '{}_{}'.format(speakerid, wav_id)
                    wav_name = '{}.wav'.format(wav_id)
                    wav_path = os.path.join(source_path, wav_name)

                    if os.path.exists(wav_path):
                        wavs[wav_id] = wav_path
                        segments[utt_id] = [wav_id]
                        transcriptions[utt_id] = transcription
                        speakers[utt_id] = speakerid

                        if gender == 'male':
                            genders[speakerid] = 'm'
                        else:
                            genders[speakerid] = 'f'

        wav_id_mapping = self.dataset.import_wavs(wavs, copy_files=True)
        utt_id_mapping = self.dataset.add_utterances(segments, wav_id_mapping=wav_id_mapping)
        speaker_id_mapping = self.dataset.set_utt2spk(genders)
        self.dataset.set_transcriptions(transcriptions, utt_id_mapping=utt_id_mapping)
        self.dataset.set_utt2spk(speakers, utt_id_mapping=utt_id_mapping, speaker_id_mapping=speaker_id_mapping)
