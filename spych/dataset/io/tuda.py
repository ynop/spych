import os

from bs4 import BeautifulSoup

from spych.dataset import segmentation
from spych.dataset import speaker
from spych.dataset.io import base


class TudaDatasetLoader(base.DatasetLoader):
    """
    Loads german tuda corpus.
    """

    @classmethod
    def type(self):
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
                        segments[utt_id] = [wav_id]
                        transcriptions[utt_id] = transcription
                        speakers[utt_id] = speakerid
                        transcriptions_raw[utt_id] = transcription_raw

                        if gender == 'male':
                            genders[speakerid] = speaker.Gender.MALE
                        elif gender == 'female':
                            genders[speakerid] = speaker.Gender.FEMALE

        # add wavs
        for wav_id, wav_path in wavs.items():
            loading_dataset.add_file(wav_path, file_idx=wav_id, copy_file=False)

        # add speakers
        for speaker_id in speakers.values():
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
            loading_dataset.add_segmentation(utt_id, segments=transcription, key=segmentation.TEXT_SEGMENTATION)

        for utt_id, transcription in transcriptions_raw.items():
            loading_dataset.add_segmentation(utt_id, segments=transcription, key=segmentation.RAW_TEXT_SEGMENTATION)
