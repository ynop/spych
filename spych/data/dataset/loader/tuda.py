import os

from bs4 import BeautifulSoup

from spych import data
from spych.data import dataset
from spych.data.dataset.loader import base


class TudaDatasetLoader(base.DatasetLoader):
    """
    Loads german tuda corpus.
    """

    @classmethod
    def type(cls):
        return 'tuda'

    def check_for_missing_files(self, path):
        return None

    def _load(self, loading_dataset):
        for part in ['train', 'dev', 'test']:
            self._import_subset(loading_dataset, part)

    def _import_subset(self, loading_dataset, part):
        source_path = os.path.join(loading_dataset.path, part)

        wavs = {}
        segments = {}
        transcriptions = {}
        transcriptions_raw = {}
        speakers = {}
        genders = {}

        for file in os.listdir(source_path):
            if file.endswith('.xml'):
                full_path = os.path.join(source_path, file)
                xml_file = open(full_path, 'r', encoding='utf-8')
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
                        segments[utt_id] = wav_id
                        transcriptions[utt_id] = str(transcription)
                        speakers[utt_id] = speakerid
                        transcriptions_raw[utt_id] = str(transcription_raw)

                        if gender == 'male':
                            genders[speakerid] = data.Gender.MALE
                        elif gender == 'female':
                            genders[speakerid] = data.Gender.FEMALE

        # add wavs
        for wav_id, wav_path in wavs.items():
            loading_dataset.add_file(wav_path, file_idx=wav_id, copy_file=False)

        # add speakers
        for speaker_id in set(speakers.values()):
            gender = None

            if speaker_id in genders.keys():
                gender = genders[speaker_id]

            loading_dataset.add_speaker(speaker_idx=speaker_id, gender=gender)

        # add utterances
        for utt_id, wav_id in segments.items():
            speaker_id = speakers[utt_id]
            loading_dataset.add_utterance(wav_id, utterance_idx=utt_id, speaker_idx=speaker_id)

        # add transcriptions
        for utt_id, transcription in transcriptions.items():
            r = loading_dataset.add_segmentation(utt_id, segments=transcription, key=data.Segmentation.TEXT_SEGMENTATION)

        for utt_id, transcription in transcriptions_raw.items():
            loading_dataset.add_segmentation(utt_id, segments=transcription, key=data.Segmentation.RAW_TEXT_SEGMENTATION)

        part_subview = dataset.Subview(filtered_utterances=set(segments.keys()))
        loading_dataset.add_subview(part, part_subview)
