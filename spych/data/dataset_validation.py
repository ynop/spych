import os
import sndhdr

from spych.data import dataset
from spych.audio import format as audio_format


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
        self.invalid_utt_ids_in_utt2spk = []

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
            if speaker_id not in self.dataset.speaker_info.keys() or dataset.SPEAKER_INFO_GENDER not in self.dataset.speaker_info[
                speaker_id].keys() or \
                            self.dataset.speaker_info[speaker_id][dataset.SPEAKER_INFO_GENDER] is None:
                self.missing_empty_genders.append(speaker_id)

        return self.missing_empty_genders

    def check_for_invalid_utt_ids_in_utt2spk(self):
        """
        Check for utterance ids in the utt2spk mapping which are not existent.

        :return: List of invalid utt ids.
        """
        self.invalid_utt_ids_in_utt2spk = []

        for utt_id in self.dataset.utt2spk.keys():
            if utt_id not in self.dataset.utterances.keys():
                self.invalid_utt_ids_in_utt2spk.append(utt_id)

        return self.invalid_utt_ids_in_utt2spk
