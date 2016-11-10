import os
import shutil
import sndhdr

from spych.audio import format as audio_format
from spych.utils import textfile
from spych.utils import jsonfile
from spych.utils import naming

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


class Dataset(object):
    """
    Speech corpus in spych format

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

    def __init__(self, dataset_folder={}, wavs={}, utterances={}, transcriptions={}, utt2spk={}, transcriptions_raw={}, speaker_info={}):
        self.path = dataset_folder
        self.wavs = dict(wavs)
        self.utterances = dict(utterances)
        self.transcriptions = dict(transcriptions)
        self.transcriptions_raw = dict(transcriptions_raw)
        self.utt2spk = dict(utt2spk)
        self.speaker_info = dict(speaker_info)

    def all_speakers(self):
        """
        Get set of all speakers.

        :return: Set
        """
        return set(self.utt2spk.values())

    def get_gender_of_speaker(self, speaker_id):
        """
        Returns gender 'm'/'f'/None

        :param speaker_id: Speaker ID
        :return: Gender
        """
        if speaker_id in self.speaker_info.keys() and SPEAKER_INFO_GENDER in self.speaker_info[speaker_id].keys():
            return self.speaker_info[speaker_id][SPEAKER_INFO_GENDER]

    def import_wavs(self, wavs, base_path=None, copy_files=False):
        """
        Import wavs into the dataset.

        :param wavs: Dictionary with wav-id/wav-path pairs.
        :param base_path: Path from where the wav-paths from wavs are valid.
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

    def add_utterances(self, utterances, wav_id_mapping=None):
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

            if wav_id_mapping and old_wav_id in wav_id_mapping.keys():
                utt_info[0] = wav_id_mapping[old_wav_id]

            self.utterances[utt_id] = utt_info

        return utt_id_mapping

    def set_transcriptions(self, transcriptions, utt_id_mapping={}):
        """
        Sets the given transcriptions.

        :param transcriptions: utt-id/transcription dict
        :param utt_id_mapping: mapping between utt-ids in the transcriptions dict and utt-ids in this dataset.
        :return:
        """
        for import_utt_id, transcription in transcriptions.items():
            utt_id = import_utt_id

            if utt_id_mapping and import_utt_id in utt_id_mapping.keys():
                utt_id = utt_id_mapping[import_utt_id]

            self.transcriptions[utt_id] = transcription

    def set_transcriptions_raw(self, transcriptions_raw, utt_id_mapping={}):
        """
        Sets the given raw transcriptions.

        :param transcriptions_raw: utt-id/transcription_raw dict
        :param utt_id_mapping: mapping between utt-ids in the raw transcriptions dict and utt-ids in this dataset.
        :return:
        """
        for import_utt_id, transcription_raw in transcriptions_raw.items():
            utt_id = import_utt_id

            if utt_id_mapping and import_utt_id in utt_id_mapping.keys():
                utt_id = utt_id_mapping[import_utt_id]

            self.transcriptions_raw[utt_id] = transcription_raw

    def set_utt2spk(self, utt2spk, utt_id_mapping=None, speaker_id_mapping=None):
        """
        Sets the speakers of the utterances.

        :param utt2spk: utt-id/speaker-id dict
        :param utt_id_mapping: mapping between utt-ids in the utt2spk dict and utt-ids in this dataset.
        :param speaker_id_mapping: mapping between speaker-ids in the utt2spk and speakers-ids in this dataset.
        :return:
        """
        for import_utt_id, import_speaker_id in utt2spk.items():
            utt_id = import_utt_id
            speaker_id = import_speaker_id

            if utt_id_mapping and import_utt_id in utt_id_mapping.keys():
                utt_id = utt_id_mapping[import_utt_id]

            if speaker_id_mapping and import_speaker_id in speaker_id_mapping.keys():
                speaker_id = speaker_id_mapping[import_speaker_id]

            self.utt2spk[utt_id] = speaker_id

    def add_speaker_info(self, speaker_info):
        """
        Sets info about speakers.

        :param speaker_info: dict speaker_id/infodict
        :return: mapping between imported speaker-id and changed id if it already existed in the dataset.
        """
        speaker_mapping = {}

        for import_speaker_id, info_dict in speaker_info.items():
            speaker_id = naming.index_name_if_in_list(import_speaker_id, self.speaker_info.keys())
            speaker_mapping[import_speaker_id] = speaker_id

            self.speaker_info[speaker_id] = info_dict

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
        speaker_id_mapping = self.add_speaker_info(dataset.speaker_info)
        self.set_transcriptions(dataset.transcriptions, utt_id_mapping=utt_id_mapping)
        self.set_utt2spk(dataset.utt2spk, utt_id_mapping=utt_id_mapping, speaker_id_mapping=speaker_id_mapping)
        self.set_transcriptions_raw(dataset.transcriptions_raw, utt_id_mapping=utt_id_mapping)

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
        utterances_path = os.path.join(path, SEGMENTS_FILE_NAME)
        transcriptions_path = os.path.join(path, TRANSCRIPTION_FILE_NAME)
        transcriptions_raw_path = os.path.join(path, TRANSCRIPTION_RAW_FILE_NAME)
        utt2spk_path = os.path.join(path, UTT2SPK_FILE_NAME)
        spk_info_path = os.path.join(path, SPEAKER_INFO_FILE_NAME)

        textfile.write_separated_lines(wav_path, self.wavs)
        self.write_utterances(utterances_path)
        textfile.write_separated_lines(transcriptions_path, self.transcriptions)
        textfile.write_separated_lines(utt2spk_path, self.utt2spk)
        jsonfile.write_json_to_file(spk_info_path, self.speaker_info)
        textfile.write_separated_lines(transcriptions_raw_path, self.transcriptions_raw)

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
        utterances_path = os.path.join(dataset_folder, SEGMENTS_FILE_NAME)
        transcriptions_path = os.path.join(dataset_folder, TRANSCRIPTION_FILE_NAME)
        transcriptions_raw_path = os.path.join(dataset_folder, TRANSCRIPTION_RAW_FILE_NAME)
        utt2spk_path = os.path.join(dataset_folder, UTT2SPK_FILE_NAME)
        spk_info_path = os.path.join(dataset_folder, SPEAKER_INFO_FILE_NAME)

        wavs = textfile.read_key_value_lines(wav_path)
        utterances = textfile.read_separated_lines_with_first_key(utterances_path, max_columns=4)
        transcriptions = {}
        transcriptions_raw = {}
        utt2spk = {}
        speaker_info = {}

        if os.path.isfile(transcriptions_path):
            transcriptions = textfile.read_key_value_lines(transcriptions_path)

        if os.path.isfile(transcriptions_raw_path):
            transcriptions_raw = textfile.read_key_value_lines(transcriptions_raw_path)

        if os.path.isfile(utt2spk_path):
            utt2spk = textfile.read_key_value_lines(utt2spk_path)

        if os.path.isfile(spk_info_path):
            speaker_info = jsonfile.read_json_file(spk_info_path)

        return cls(dataset_folder=dataset_folder,
                   wavs=wavs,
                   utterances=utterances,
                   transcriptions=transcriptions,
                   utt2spk=utt2spk,
                   transcriptions_raw=transcriptions_raw,
                   speaker_info=speaker_info)

    def write_utterances(self, path):
        """
        Writes the utterances to the file at the given path.
        -1 if start/end is not given or is None.

        :param path: Path
        """
        f = open(path, 'w')

        for utt_id in sorted(self.utterances.keys()):
            value = self.utterances[utt_id]

            wav_id = value[0]
            start = -1
            end = -1

            if len(value) > 1 and value[1] is not None:
                start = value[1]

            if len(value) > 2 and value[2] is not None:
                end = value[2]

            f.write('{} {} {} {}\n'.format(utt_id, wav_id, start, end))

        f.close()


class DatasetValidation(object):
    """
    Class to validate a dataset.

    Checks different things. But you don't get a true/false result, because that depends on the use case.
    """

    def __init__(self, dataset, expected_wav_format=audio_format.AudioFileFormat.wav_mono_16bit_16k()):
        self.dataset = dataset
        self.expected_wav_format = expected_wav_format

        self.missing_wavs = []
        self.wavs_with_wrong_format = []
        self.wavs_without_utterances = []
        self.utterances_with_missing_wav_id = []
        self.missing_empty_transcriptions = []
        self.missing_empty_speakers = []
        self.missing_empty_genders = []

    def run_all_checks(self):
        """
        Runs all checks. Results can be obtained via instance variables.

        :return:
        """
        self.check_for_missing_wav_files()
        self.check_for_wavs_with_wrong_format()
        self.check_for_wavs_without_utterances()
        self.check_for_utterances_with_wav_id_missing()
        self.check_for_missing_transcriptions()
        self.check_for_missing_speakers()
        self.check_for_missing_gender()

    def check_for_missing_wav_files(self):
        """
        Checks if the wav files referenced in the wav.txt are existing.

        :return: dict with missing wav-files wav-id/path
        """
        self.missing_wavs = []

        for wav_id, wav_path in self.dataset.wavs.items():
            full_path = os.path.join(self.dataset.path, wav_path)

            if not os.path.isfile(full_path):
                self.missing_wavs.append(wav_id)

        return self.missing_wavs

    def check_for_wavs_with_wrong_format(self):
        """
        Check for wav files with wrong format.

        :param expected_format: the format the wav files should match
        :return: List of wav-ids with wrong formatted files.
        """
        self.wavs_with_wrong_format = []

        for wav_id, wav_path in self.dataset.wavs.items():
            full_path = os.path.join(self.dataset.path, wav_path)

            if os.path.isfile(full_path):
                result = sndhdr.what(full_path)

                if result is None or not self.expected_wav_format.matches_sound_header(result):
                    self.wavs_with_wrong_format.append(wav_id)

        return self.wavs_with_wrong_format

    def check_for_wavs_without_utterances(self):
        """
        Check if there are any wavs without any utterances.

        :return: List of wav-ids without corresponding utterances.
        """
        wavs_with_utterances = set()

        for utt_id, info in self.dataset.utterances.items():
            if len(info) > 0:
                if info is not None:
                    wavs_with_utterances.add(info[0])

        self.wavs_without_utterances = list(set(self.dataset.wavs.keys()) - wavs_with_utterances)

        return self.wavs_without_utterances

    def check_for_utterances_with_wav_id_missing(self):
        """
        Check if there are any utterances that reference a wav-id that isn't existing.

        :return: List of utterance-ids with wrong wav-id references.
        """
        self.utterances_with_missing_wav_id = []

        for utt_id, info in self.dataset.utterances.items():
            if len(info) > 0:
                if info[0] is None or info[0] not in self.dataset.wavs.keys():
                    self.utterances_with_missing_wav_id.append(utt_id)
            else:
                self.utterances_with_missing_wav_id.append(utt_id)

        return self.utterances_with_missing_wav_id

    def check_for_missing_transcriptions(self):
        """
        Check for missing or empty transcriptions.

        :return: List of utt-id with missing or empty transcriptions.
        """
        self.missing_empty_transcriptions = []

        for utt_id in self.dataset.utterances.keys():
            if utt_id not in self.dataset.transcriptions.keys() or self.dataset.transcriptions[utt_id] in [None, '']:
                self.missing_empty_transcriptions.append(utt_id)

        return self.missing_empty_transcriptions

    def check_for_missing_speakers(self):
        """
        Check for missing or empty speakers.

        :return: List of utt-id with missing or empty speakers.
        """
        self.missing_empty_speakers = []

        for utt_id in self.dataset.utterances.keys():
            if utt_id not in self.dataset.utt2spk.keys() or self.dataset.utt2spk[utt_id] in [None, '']:
                self.missing_empty_speakers.append(utt_id)

        return self.missing_empty_speakers

    def check_for_missing_gender(self):
        """
        Check for missing or empty genders.

        :return: List of utt-id with missing or empty genders.
        """
        self.missing_empty_genders = []

        for speaker_id in self.dataset.all_speakers():
            if speaker_id not in self.dataset.speaker_info.keys() or SPEAKER_INFO_GENDER not in self.dataset.speaker_info[speaker_id].keys() or \
                            self.dataset.speaker_info[speaker_id][SPEAKER_INFO_GENDER] is None:
                self.missing_empty_genders.append(speaker_id)

        return self.missing_empty_genders
