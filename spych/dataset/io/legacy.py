import os

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
    """
    Loads dataset from the old spych format.

    wavs.txt
    --------------------------------
    [wav-id] [relative-wav-path]

    utterances.txt
    --------------------------------
    [utt-id] [wav-id] [start] [end]

    transcriptions.txt
    --------------------------------
    [utt-id] [transcription]

    transcriptions_raw.txt
    --------------------------------
    [utt-id] [transcription raw]

    Transcription with punctuation.

    utt2spk.txt
    --------------------------------
    [utt-id] [speaker-id]

    speaker_info.json
    --------------------------------
    {
        "speaker_id" : {
            "gender" : "m"/"f",
            ...
        },
        ...
    }
    """

    def type(self):
        return 'legacy_spych'

    def is_valid_folder(self, path):
        necessary_files = [WAV_FILE_NAME, SEGMENTS_FILE_NAME]
        missing_files = []

        for file_name in necessary_files:
            file_path = os.path.join(path, file_name)

            if not os.path.isfile(file_path):
                missing_files.append(file_name)

        return missing_files or None

    #
    #  Load
    #

    def _load(self, loading_dataset):
        self._load_wavs(loading_dataset)
        self._load_utterances(loading_dataset)
        self._load_transcriptions(loading_dataset)
        self._load_speakers(loading_dataset)

    def _load_wavs(self, loading_dataset):
        wav_path = os.path.join(loading_dataset, WAV_FILE_NAME)

        for wav_id, wav_path in textfile.read_key_value_lines(wav_path):
            loading_dataset.add_file(wav_path, file_idx=wav_id)

    def _load_utterances(self, loading_dataset):
        utterances_path = os.path.join(loading_dataset.path, SEGMENTS_FILE_NAME)
        for utt_id, utt_info in textfile.read_separated_lines_with_first_key(utterances_path, max_columns=4):
            start = utterance.START_FULL_FILE
            end = utterance.END_FULL_FILE

            if len(utt_info) > 1:
                start = utt_info[1]

            if len(utt_info) > 2:
                end = utt_info[2]

            loading_dataset.add_utterance(utt_info[0], utterance_idx=utt_id, start=start, end=end)

    def _load_transcriptions(self, loading_dataset):
        transcriptions_path = os.path.join(loading_dataset.path, TRANSCRIPTION_FILE_NAME)
        transcriptions_raw_path = os.path.join(loading_dataset.path, TRANSCRIPTION_RAW_FILE_NAME)

        if os.path.isfile(transcriptions_path):
            for utt_id, transcription in textfile.read_key_value_lines(transcriptions_path):
                loading_dataset.add_segmentation(utt_id, segments=transcription, key=segmentation.TEXT_SEGMENTATION)

        if os.path.isfile(transcriptions_raw_path):
            for utt_id, transcription_raw in textfile.read_key_value_lines(transcriptions_raw_path):
                loading_dataset.add_segmentation(utt_id, segments=transcription_raw, key=segmentation.RAW_TEXT_SEGMENTATION)

    def _load_speakers(self, loading_dataset):
        utt2spk_path = os.path.join(loading_dataset.path, UTT2SPK_FILE_NAME)
        spk_info_path = os.path.join(loading_dataset.path, SPEAKER_INFO_FILE_NAME)

        if os.path.isfile(spk_info_path):
            for spk_id, spk_info in jsonfile.read_json_file(spk_info_path):
                spk_obj = loading_dataset.add_speaker(speaker_idx=spk_id)
                spk_obj.load_speaker_info_from_dict(spk_info)

        if os.path.isfile(utt2spk_path):
            for utt_id, spk_id in textfile.read_key_value_lines(utt2spk_path):
                loading_dataset.utterances[utt_id].speaker_idx = spk_id
