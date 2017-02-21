import os

from spych.dataset.io import base
from spych.dataset import speaker
from spych.dataset import segmentation

from spych.utils import textfile

WAV_FILE_NAME = 'wavs.scp'
SEGMENTS_FILE_NAME = 'segments'
UTT2SPK_FILE_NAME = 'utt2spk'
SPK2GENDER_FILE_NAME = 'spk2gender'
TRANSCRIPTION_FILE_NAME = 'text'


class SpychDatasetLoader(base.DatasetLoader):
    def type(self):
        return 'kaldi'

    def check_for_missing_files(self, path):
        necessary_files = [WAV_FILE_NAME, TRANSCRIPTION_FILE_NAME]
        missing_files = []

        for file_name in necessary_files:
            file_path = os.path.join(path, file_name)

            if not os.path.isfile(file_path):
                missing_files.append(file_name)

        return missing_files or None

    def _load(self, dataset):
        # load wavs
        wav_file_path = os.path.join(dataset.path, WAV_FILE_NAME)
        for file_idx, file_path in textfile.read_key_value_lines(wav_file_path, separator=' ').items():
            dataset.add_file(file_path, file_idx=file_idx)

        # load utterances
        utt2spk_path = os.path.join(dataset.path, UTT2SPK_FILE_NAME)
        utt2spk = {}

        if os.path.isfile(utt2spk_path):
            utt2spk = textfile.read_key_value_lines(utt2spk_path, separator=' ')

        segments_path = os.path.join(dataset.path, SEGMENTS_FILE_NAME)

        if os.path.isfile(segments_path):
            for utt_id, utt_info in textfile.read_separated_lines_with_first_key(segments_path, separator=' ', max_columns=4).items():
                start = None
                end = None

                if len(utt_info) > 1:
                    start = utt_info[1]

                if len(utt_info) > 2:
                    end = utt_info[2]

                speaker_idx = None

                if utt_id in utt2spk.keys():
                    speaker_idx = utt2spk[utt_id]

                dataset.add_utterance(utt_info[0], utterance_idx=utt_id, speaker_idx=speaker_idx, start=start, end=end)
        else:
            for file_idx in dataset.files.keys():
                speaker_idx = None

                if file_idx in utt2spk.keys():
                    speaker_idx = utt2spk[file_idx]

                dataset.add_utterance(file_idx, utterance_idx=file_idx, speaker_idx=speaker_idx)

        # load transcriptions
        text_path = os.path.join(dataset.path, TRANSCRIPTION_FILE_NAME)
        for utt_id, transcription in textfile.read_key_value_lines(text_path, separator=' ').items():
            dataset.add_segmentation(utt_id, segments=transcription)

        # load genders
        gender_path = os.path.join(dataset.path, SPK2GENDER_FILE_NAME)
        for spk_id, gender in textfile.read_key_value_lines(gender_path, separator=' ').items():
            if spk_id in dataset.speakers.keys():
                spk = dataset.speakers[spk_id]

                if gender == 'm':
                    spk.gender = speaker.Gender.MALE
                elif gender == 'f':
                    spk.gender = speaker.Gender.FEMALE

    def save(self, dataset, path):
        # Write files
        file_path = os.path.join(path, WAV_FILE_NAME)
        file_records = {file.idx: file.path for file in dataset.files.values()}
        textfile.write_separated_lines(file_path, file_records, separator=' ', sort_by_column=0)

        # Write utterances
        utterance_path = os.path.join(path, SEGMENTS_FILE_NAME)
        utterance_records = {utterance.idx: [utterance.file_idx, utterance.start, utterance.end] for utterance in dataset.utterances.values()}
        textfile.write_separated_lines(utterance_path, utterance_records, separator=' ', sort_by_column=0)

        # Write utt2spk
        utt2spk_path = os.path.join(path, UTT2SPK_FILE_NAME)
        utt2spk_records = {utterance.idx: utterance.speaker_idx for utterance in dataset.utterances.values()}
        textfile.write_separated_lines(utt2spk_path, utt2spk_records, separator=' ', sort_by_column=0)

        # Write speakers
        gender_path = os.path.join(path, SPK2GENDER_FILE_NAME)
        speaker_data = {spk.idx: spk.gender for spk in dataset.speakers.values()}
        textfile.write_separated_lines(gender_path, speaker_data, separator=' ', sort_by_column=0)

        # Write segmentations
        transcriptions = {}

        for utterance_idx, utt_segmentations in dataset.segmentations.items():
            if segmentation.TEXT_SEGMENTATION in utt_segmentations.keys():
                transcriptions[utterance_idx] = utt_segmentations[segmentation.TEXT_SEGMENTATION].to_text()

        text_path = os.path.join(path, TRANSCRIPTION_FILE_NAME)
        textfile.write_separated_lines(text_path, transcriptions, separator=' ', sort_by_column=0)
