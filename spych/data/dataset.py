import os

from spych.utils import textfile

WAV_FILE_NAME = 'wavs.txt'
SEGMENTS_FILE_NAME = 'segments.txt'
TRANSCRIPTION_FILE_NAME = 'text.txt'
UTT2SPK_FILE_NAME = 'utt2spk.txt'
SPEAKERS_FILE_NAME = 'speakers.txt'


class Dataset(object):
    """
    Speech corpus in spych format

    wavs.txt
    ----------------
    [wav-id] [relative-wav-path]

    segments.txt
    ----------------
    [utt-id] [wav-id] [start] [end]

    text.txt
    ----------------
    [utt-id] [transcription]

    utt2spk.txt
    ----------------
    [utt-id] [speaker-id]

    speakers.txt
    ----------------
    [speaker-id] [gender]


    """

    def __init__(self, dataset_folder=None, wavs={}, utterances={}, transcriptions={}, utt2spk={}, speakers={}):
        self.path = dataset_folder
        self.wavs = wavs
        self.utterances = utterances
        self.transcriptions = transcriptions
        self.utt2spk = utt2spk
        self.speakers = speakers

    #
    #   READ / WRITE
    #

    def save(self):
        self.save_to_path(self.path)

    def save_to_path(self, path):
        os.makedirs(path, exist_ok=True)

        wav_path = os.path.join(path, WAV_FILE_NAME)
        segments_path = os.path.join(path, SEGMENTS_FILE_NAME)
        transcriptions_path = os.path.join(path, TRANSCRIPTION_FILE_NAME)
        utt2spk_path = os.path.join(path, UTT2SPK_FILE_NAME)
        speakers_path = os.path.join(path, SPEAKERS_FILE_NAME)

        textfile.write_separated_lines(wav_path, self.wavs)
        textfile.write_separated_lines(segments_path, self.utterances)
        textfile.write_separated_lines(transcriptions_path, self.transcriptions)
        textfile.write_separated_lines(utt2spk_path, self.utt2spk)
        textfile.write_separated_lines(speakers_path, self.speakers)

    @classmethod
    def load_from_path(cls, path):
        dataset_folder = os.path.abspath(path)

        necessary_files = [WAV_FILE_NAME, SEGMENTS_FILE_NAME]

        for file_name in necessary_files:
            file_path = os.path.join(dataset_folder, file_name)

            if not os.path.isfile(file_path):
                raise IOError('Invalid dataset: file not found {}'.format(file_name))

        wav_path = os.path.join(dataset_folder, WAV_FILE_NAME)
        segments_path = os.path.join(dataset_folder, SEGMENTS_FILE_NAME)
        transcriptions_path = os.path.join(dataset_folder, TRANSCRIPTION_FILE_NAME)
        utt2spk_path = os.path.join(dataset_folder, UTT2SPK_FILE_NAME)
        speakers_path = os.path.join(dataset_folder, SPEAKERS_FILE_NAME)

        wavs = textfile.read_key_value_lines(wav_path)
        utterances = textfile.read_separated_lines_with_first_key(segments_path, max_columns=4)
        transcriptions = {}
        utt2spk = {}
        speakers = {}

        if os.path.isfile(transcriptions_path):
            transcriptions = textfile.read_key_value_lines(transcriptions_path)

        if os.path.isfile(utt2spk_path):
            utt2spk = textfile.read_key_value_lines(utt2spk_path)

        if os.path.isfile(speakers_path):
            speakers = textfile.read_key_value_lines(speakers_path)

        return cls(dataset_folder, wavs, utterances, transcriptions, utt2spk, speakers)
