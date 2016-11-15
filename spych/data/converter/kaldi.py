import os
import shutil

from spych.data import dataset
from spych.utils import textfile

WAV_NAME = 'wav.scp'
SEGMENTS_NAME = 'segments'
TRANSCRIPTION_NAME = 'text'
UTT2SPK_NAME = 'utt2spk'
SPK2GENDER_NAME = 'spk2gender'


class KaldiExporter(object):
    def __init__(self, target_folder, dataset, copy_wavs=False):
        self.target_folder = target_folder
        self.dataset = dataset
        self.copy_wavs = copy_wavs

    def run(self):
        os.makedirs(self.target_folder)

        spk2gender = {}
        wavs = {}

        for speaker_id, info in self.dataset.speaker_info.items():
            if dataset.SPEAKER_INFO_GENDER in info:
                spk2gender[speaker_id] = info[dataset.SPEAKER_INFO_GENDER]

        for wav_id, wav_rel_path in self.dataset.wavs.items():
            wav_abs_path = os.path.abspath(os.path.join(self.dataset.path, wav_rel_path))
            if self.copy_wavs:
                wav_name = os.path.basename(wav_rel_path)
                target_wav_path = os.path.abspath(os.path.join(self.target_folder, wav_name))
                shutil.copy(wav_abs_path, target_wav_path)
                wavs[wav_id] = target_wav_path
            else:
                wavs[wav_id] = wav_abs_path

        textfile.write_separated_lines(os.path.join(self.target_folder, WAV_NAME), wavs, separator=' ')
        self.write_utterances()
        textfile.write_separated_lines(os.path.join(self.target_folder, TRANSCRIPTION_NAME), self.dataset.transcriptions, separator=' ')
        textfile.write_separated_lines(os.path.join(self.target_folder, UTT2SPK_NAME), self.dataset.utt2spk, separator=' ')
        textfile.write_separated_lines(os.path.join(self.target_folder, SPK2GENDER_NAME), spk2gender, separator=' ')

    def write_utterances(self):
        """
        Writes the utterances to the file.
        -1 if start/end is not given or is None.
        """

        f = open(os.path.join(self.target_folder, SEGMENTS_NAME), 'w')

        for utt_id in sorted(self.dataset.utterances.keys()):
            value = self.dataset.utterances[utt_id]

            wav_id = value[0]
            start = -1
            end = -1

            if len(value) > 1 and value[1] is not None:
                start = value[1]

            if len(value) > 2 and value[2] is not None:
                end = value[2]

            f.write('{} {} {} {}\n'.format(utt_id, wav_id, start, end))

        f.close()
