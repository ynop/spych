import os
import shutil

from spych.utils import textfile
from spych.utils import naming

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

    def import_wavs(self, wavs={}, base_path=None, copy_files=False):
        """
        Import wavs into the dataset.

        :param wavs: Dictionary with wav-id/wav-path pairs.
        :param copy_files: If the wav files should be copied into this dataset directory.
        :return: Mapping between old-wav-id and new-wav-id (in case some id already existed in this dataset it can be looked up)
        """
        wav_id_map = {}

        for import_wav_id, import_relative_wav_path in wavs.items():
            wav_id = naming.index_name_if_in_list(import_wav_id, self.wavs.keys())
            wav_id_map[import_wav_id] = wav_id

            import_wav_path = import_relative_wav_path

            if base_path is not None:
                import_wav_path = os.path.abspath(os.path.join(base_path, import_relative_wav_path))
            wav_path = import_wav_path

            if copy_files:
                import_wav_file_basename, import_wav_file_extension = os.path.splitext(os.path.basename(import_wav_path))
                wav_file_name = naming.index_name_if_in_list(import_wav_file_basename, self.wavs.values(), suffix=import_wav_file_extension)
                wav_path = os.path.join(self.path, wav_file_name)
                shutil.copy(import_wav_path, wav_path)

            relative_wav_path = os.path.relpath(wav_path, self.path)

            self.wavs[wav_id] = relative_wav_path

        return wav_id_map

    def add_utterances(self, utterances={}, wav_id_mapping={}):
        """
        Adds the given utterances to the dataset.

        :param utterances: Utterances dict utt-id/[wav-id, start, end]
        :param wav_id_mapping: Mapping between imported wav-ids and existing wav-ids in the dataset.
        :return: mapping between imported utt-id and changed id if it already existed in the dataset.
        """
        utt_id_mapping = {}

        for import_utt_id, import_utt_info in utterances.items():
            utt_id = naming.index_name_if_in_list(import_utt_id, self.utterances.keys())
            utt_info = list(import_utt_info)
            utt_id_mapping[import_utt_id] = utt_id

            old_wav_id = utt_info[0]

            if old_wav_id in wav_id_mapping.keys():
                utt_info[0] = wav_id_mapping[old_wav_id]

            self.utterances[utt_id] = utt_info

        return utt_id_mapping

    def set_transcriptions(self, transcriptions={}, utt_id_mapping={}):
        """
        Sets the given transcriptions.

        :param transcriptions: utt-id/transcription dict
        :param utt_id_mapping: mapping between utt-ids in the transcriptions dict and utt-ids in this dataset.
        :return:
        """
        for import_utt_id, transcription in transcriptions.items():
            utt_id = import_utt_id

            if import_utt_id in utt_id_mapping.keys():
                utt_id = utt_id_mapping[import_utt_id]

            self.transcriptions[utt_id] = transcription

    def set_utt2spk(self, utt2spk={}, utt_id_mapping={}, speaker_id_mapping={}):
        """
        Sets the speakers of the utterances.

        :param utt2spk: utt-id/speaker-id dict
        :param utt_id_mapping: mapping between utt-ids in the utt2spk dict and utt-ids in this dataset.
        :return:
        """
        for import_utt_id, import_speaker_id in utt2spk.items():
            utt_id = import_utt_id
            speaker_id = import_speaker_id

            if import_utt_id in utt_id_mapping.keys():
                utt_id = utt_id_mapping[import_utt_id]

            if import_speaker_id in speaker_id_mapping.keys():
                speaker_id = speaker_id_mapping[import_speaker_id]

            self.utt2spk[utt_id] = speaker_id

    def set_speakers(self, speakers={}):
        """
        Set genders of the speakers.

        :param speakers: speaker-id/gender dict
        :return: mapping between imported speaker-id and changed id if it already existed in the dataset.
        """
        speaker_mapping = {}

        for import_speaker, info in speakers.items():
            speaker = naming.index_name_if_in_list(import_speaker, self.speakers.keys())
            speaker_mapping[import_speaker] = speaker

            self.speakers[speaker] = info

        return speaker_mapping

    def merge_dataset(self, dataset, copy_wavs=False):
        """
        Merges the given dataset into this dataset.

        :param dataset: Dataset to merge
        :param copy_wavs: If True moves the wavs to this datasets folder
        :return:
        """
        wav_id_mapping = self.import_wavs(dataset.wavs, base_path=dataset.path, copy_files=copy_wavs)
        utt_id_mapping = self.add_utterances(dataset.utterances, wav_id_mapping=wav_id_mapping)
        speaker_id_mapping = self.set_speakers(speakers=self.speakers)
        self.set_transcriptions(dataset.transcriptions, utt_id_mapping=utt_id_mapping)
        self.set_utt2spk(dataset.utt2spk, utt_id_mapping=utt_id_mapping, speaker_id_mapping=speaker_id_mapping)

    #
    #   READ / WRITE
    #

    def save(self):
        """
        Saves the dataset.
        """
        self.save_to_path(self.path)

    def save_to_path(self, path):
        """
        Saves the dataset to the given path.

        :param path: Directory to store the dataset (will be created if it doesnt exist).
        """
        if self.path is None or self.path == '':
            raise ValueError('No path given to save dataset')

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
        """
        Loads dataset from the given path.

        :param path: Directory to load dataset from.
        :return:
        """
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
