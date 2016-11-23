import os
import shutil
import collections

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

    def name(self):
        """
        Get the name of the dataset (= basename)
        :return: name
        """
        return os.path.basename(self.path)

    def all_speakers(self):
        """
        Get set of all speakers.

        :return: Set
        """
        return set(self.utt2spk.values())

    def utterances_of_wav(self, wav_id):
        """
        Returns all utterances that are in the given wav.

        :param wav_id: Wav ID
        :return: Set of uttIDs
        """
        utt_ids = set()

        for utt_id, info in self.utterances.items():
            wid = info[0]

            if wid == wav_id:
                utt_ids.add(utt_id)

        return utt_ids

    def utterances_of_speaker(self, speaker_id):
        """
        Returns all utterance-ids of the given speaker.

        :param speaker_id: Speaker ID
        :return: Set of uttIDs
        """
        utt_ids = set()

        for utt_id, utt_speaker_id in self.utt2spk.items():
            if utt_speaker_id == speaker_id:
                utt_ids.add(utt_id)

        return utt_ids

    def get_gender_of_speaker(self, speaker_id):
        """
        Returns gender 'm'/'f'/None

        :param speaker_id: Speaker ID
        :return: Gender
        """
        if speaker_id in self.speaker_info.keys() and SPEAKER_INFO_GENDER in self.speaker_info[speaker_id].keys():
            return self.speaker_info[speaker_id][SPEAKER_INFO_GENDER]

    def get_speaker_to_utterances(self):
        """
        Returns the mapping between speakers and utterances.

        :return: dict [speaker/list of utterance-ids]
        """
        spk2utt = collections.defaultdict(list)

        for utt_id, speaker_id in self.utt2spk.items():
            spk2utt[speaker_id].append(utt_id)

        return spk2utt

    def utterance_has_transcription(self, utt_id):
        """
        Return whether the utterance with the given id has a transcription.

        :param utt_id: Utterance ID
        :return: True if has transcription
        """
        return utt_id in self.transcriptions.keys()

    def utterance_has_transcription_raw(self, utt_id):
        """
        Return whether the utterance with the given id has a raw transcription.

        :param utt_id: Utterance ID
        :return: True if has raw transcription
        """
        return utt_id in self.transcriptions_raw.keys()

    def utterance_has_speaker(self, utt_id):
        """
        Return whether the utterance with the given id has a speaker.

        :param utt_id: Utterance ID
        :return: True if has raw speaker
        """
        return utt_id in self.utt2spk.keys()

    def speaker_has_info(self, speaker_id):
        """
        Return whether the speaker with the given id has info dict.

        :param speaker_id: Speaker ID
        :return: True if has info dict
        """
        return speaker_id in self.speaker_info.keys()

    def remove_wavs(self, wavs, remove_files=False):
        """
        Deletes the given wavs.

        :param wavs: List of wavids
        :param remove_files: Also delete the files
        """

        for wav_id in wavs:
            if remove_files:
                path = os.path.join(self.path, self.wavs[wav_id])
                if os.path.exists(path):
                    os.remove(path)

            utt_ids_to_delete = self.utterances_of_wav(wav_id)

            self.remove_utterances(utt_ids_to_delete)

            del self.wavs[wav_id]

    def remove_utterances(self, utterances):
        """
        Removes the given utterances by id.

        :param utterances: list of utterance ids
        """
        for utt_id in utterances:
            del self.utterances[utt_id]
            del self.transcriptions[utt_id]
            del self.utt2spk[utt_id]
            del self.transcriptions_raw[utt_id]

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
            start = 0
            end = -1

            if len(value) > 1 and value[1] is not None:
                if int(value[1]) < 0:
                    start = 0
                else:
                    start = value[1]

            if len(value) > 2 and value[2] is not None:
                end = value[2]

            f.write('{} {} {} {}\n'.format(utt_id, wav_id, start, end))

        f.close()
