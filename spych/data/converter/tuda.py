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

        self._create_dataset()
        self.dataset.save()

        return self.dataset

    def _create_dataset(self):
        for part in ['train', 'dev', 'test']:
            subset = self._create_subset(part)
            self.dataset.merge_dataset(subset, copy_wavs=False)

    def _create_subset(self, name):
        source_path = os.path.join(self.source_folder, name)
        target_path = os.path.join(self.target_folder, name)

        wavs = {}
        segments = {}
        transcriptions = {}
        transcriptions_raw = {}
        speakers = {}
        speaker_info = {}

        for file in os.listdir(source_path):
            if file.endswith('.xml'):
                full_path = os.path.join(source_path, file)
                xml_file = open(full_path, 'r')
                soup = BeautifulSoup(xml_file, "lxml")
                xml_id, __ = os.path.splitext(file)
                transcription = soup.recording.cleaned_sentence.string
                transcription_raw = soup.recording.sentence.string
                gender = soup.recording.gender.string
                speakerid = soup.recording.speaker_id.string

                for mic in ['Kinect-Beam', 'Kinect-RAW', 'Realtek', 'Samson', 'Yamaha']:
                    wav_id = '{}_{}'.format(xml_id, mic)
                    utt_id = '{}_{}'.format(speakerid, wav_id)
                    wav_name = '{}.wav'.format(wav_id)
                    wav_path = os.path.join(source_path, wav_name)

                    if os.path.exists(wav_path):
                        wavs[wav_id] = wav_path
                        segments[utt_id] = [wav_id]
                        transcriptions[utt_id] = transcription
                        speakers[utt_id] = speakerid
                        transcriptions_raw[utt_id] = transcription_raw

                        if gender == 'male':
                            speaker_info[speakerid] = {
                                dataset.SPEAKER_INFO_GENDER: 'm'
                            }
                        elif gender == 'female':
                            speaker_info[speakerid] = {
                                dataset.SPEAKER_INFO_GENDER: 'f'
                            }

        subset = dataset.Dataset(dataset_folder=target_path)
        subset.save()

        wav_id_mapping = subset.import_wavs(wavs, copy_files=True)
        utt_id_mapping = subset.add_utterances(segments, wav_id_mapping=wav_id_mapping)
        speaker_id_mapping = subset.add_speaker_info(speaker_info)
        subset.set_transcriptions(transcriptions, utt_id_mapping=utt_id_mapping)
        subset.set_transcriptions_raw(transcriptions_raw, utt_id_mapping=utt_id_mapping)
        subset.set_utt2spk(speakers, utt_id_mapping=utt_id_mapping, speaker_id_mapping=speaker_id_mapping)

        return subset
