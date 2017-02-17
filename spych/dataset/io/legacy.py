import os

from spych.dataset import dataset
from spych.dataset import utterance
from spych.dataset import segmentation
from spych.dataset.io import base

from spych.utils import textfile
from spych.utils import jsonfile

WAV_FILE_NAME = 'wavs.txt'
SEGMENTS_FILE_NAME = 'utterances.txt'
TRANSCRIPTION_FILE_NAME = 'transcriptions.txt'
TRANSCRIPTION_RAW_FILE_NAME = 'transcriptions_raw.txt'
UTT2SPK_FILE_NAME = 'utt2spk.txt'
SPEAKER_INFO_FILE_NAME = 'speaker_info.json'

SPEAKER_INFO_GENDER = 'gender'
SPEAKER_INFO_SYNTHESIZED = 'synthesized'
SPEAKER_INFO_SYNTHESIZER_VOICE = 'synthesizer_voice'
SPEAKER_INFO_SYNTHESIZER_EFFECTS = 'synthesizer_effects'
SPEAKER_INFO_SYNTHESIZER_TOOL = 'synthesizer_tool'


class LegacySpychDatasetLoader(base.DatasetLoader):
    def type(self):
        return 'legacy_spych'

    def load(self, path):
        necessary_files = [WAV_FILE_NAME, SEGMENTS_FILE_NAME]

        for file_name in necessary_files:
            file_path = os.path.join(path, file_name)

            if not os.path.isfile(file_path):
                raise IOError('Invalid dataset: file not found {}'.format(file_name))

        wav_path = os.path.join(path, WAV_FILE_NAME)
        utterances_path = os.path.join(path, SEGMENTS_FILE_NAME)
        transcriptions_path = os.path.join(path, TRANSCRIPTION_FILE_NAME)
        transcriptions_raw_path = os.path.join(path, TRANSCRIPTION_RAW_FILE_NAME)
        utt2spk_path = os.path.join(path, UTT2SPK_FILE_NAME)
        spk_info_path = os.path.join(path, SPEAKER_INFO_FILE_NAME)

        loading_dataset = dataset.Dataset(path)

        for wav_id, wav_path in textfile.read_key_value_lines(wav_path):
            loading_dataset.add_file(wav_path, file_idx=wav_id)

        for utt_id, utt_info in textfile.read_separated_lines_with_first_key(utterances_path, max_columns=4):
            start = utterance.START_FULL_FILE
            end = utterance.END_FULL_FILE

            if len(utt_info) > 1:
                start = utt_info[1]

            if len(utt_info) > 2:
                end = utt_info[2]

            loading_dataset.add_utterance(utt_info[0], utterance_idx=utt_id, start=start, end=end)

        if os.path.isfile(transcriptions_path):
            for utt_id, transcription in textfile.read_key_value_lines(transcriptions_path):
                loading_dataset.add_segmentation(utt_id, segments=transcription, key=segmentation.TEXT_SEGMENTATION)

        if os.path.isfile(transcriptions_raw_path):
            for utt_id, transcription_raw in textfile.read_key_value_lines(transcriptions_raw_path):
                loading_dataset.add_segmentation(utt_id, segments=transcription_raw, key=segmentation.RAW_TEXT_SEGMENTATION)

        if os.path.isfile(spk_info_path):
            for spk_id, spk_info in jsonfile.read_json_file(spk_info_path):
                spk_obj = loading_dataset.add_speaker(speaker_idx=spk_id)
                spk_obj.load_speaker_info_from_dict(spk_info)

        if os.path.isfile(utt2spk_path):
            for utt_id, spk_id in textfile.read_key_value_lines(utt2spk_path):
                loading_dataset.utterances[utt_id].speaker_idx = spk_id
