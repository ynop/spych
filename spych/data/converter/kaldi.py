import os
import shutil

from spych.data import dataset
from spych.utils import textfile

WAV_NAME = 'wav.scp'
SEGMENTS_NAME = 'segments'
TRANSCRIPTION_NAME = 'text'
UTT2SPK_NAME = 'utt2spk'
SPK2GENDER_NAME = 'spk2gender'


class KaldiConverter(object):
    def __init__(self, target_folder, source_folder, copy_wavs=True):
        self.target_folder = target_folder
        self.source_folder =source_folder
        self.copy_wavs=copy_wavs
        self.dataset = None

    def run(self):
        wav_file_path = os.path.join(self.source_folder, WAV_NAME)
        segements_file_path = os.path.join(self.source_folder, SEGMENTS_NAME)
        transcription_file_path = os.path.join(self.source_folder, TRANSCRIPTION_NAME)
        utt2spk_file_path = os.path.join(self.source_folder, UTT2SPK_NAME)
        spk2gender_file_path = os.path.join(self.source_folder, SPK2GENDER_NAME)

        wavs_in=textfile.read_key_value_lines(wav_file_path, separator=' ')
        utt2spk_in=textfile.read_key_value_lines(utt2spk_file_path, separator=' ')
        spk2gender=textfile.read_key_value_lines(spk2gender_file_path, separator=' ')
        transcriptions_in=textfile.read_key_value_lines(transcription_file_path, separator=' ')

        wavs={}

        for wav_id, wav_path in wavs_in.items():
            wavs[wav_id] = os.path.abspath(os.path.join(self.source_folder, wav_path))

        if os.path.exists(segements_file_path):
            segements=textfile.read_separated_lines_with_first_key(segements_file_path, separator=' ')
            utt2spk = utt2spk_in
            transcriptions=transcriptions_in
        else:
            segements={}
            utt2spk={}
            transcriptions={}

            for wav_id, wav_path in wavs.items():
                spk_id = utt2spk_in[wav_id]
                utt_id = '{}-{}'.format(spk_id, wav_id)
                segements[utt_id] = [wav_id]
                utt2spk[utt_id] = spk_id
                transcriptions[utt_id] = transcriptions_in[wav_id]


        spk_info={}

        for spk_id, gender in spk2gender.items():
            spk_info[spk_id] = {
                dataset.SPEAKER_INFO_GENDER: gender
            }


        self.dataset = dataset.Dataset(dataset_folder=self.target_folder)
        self.dataset.save()

        wav_id_mapping = self.dataset.import_wavs(wavs, copy_files=self.copy_wavs)
        utt_id_mapping = self.dataset.add_utterances(segements, wav_id_mapping=wav_id_mapping)
        speaker_id_mapping = self.dataset.add_speaker_info(spk_info)
        self.dataset.set_transcriptions(transcriptions, utt_id_mapping=utt_id_mapping)
        self.dataset.set_utt2spk(utt2spk, utt_id_mapping=utt_id_mapping, speaker_id_mapping=speaker_id_mapping)

        self.dataset.save()

        return self.dataset

class KaldiExporter(object):
    def __init__(self, target_folder, dataset, copy_wavs=False):
        self.target_folder = target_folder
        self.dataset = dataset
        self.copy_wavs = copy_wavs

    def run(self):
        os.makedirs(self.target_folder, exist_ok=True)

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

        f = open(os.path.join(self.target_folder, SEGMENTS_NAME), 'w', encoding='utf-8')

        for utt_id in sorted(self.dataset.utterances.keys()):
            value = self.dataset.utterances[utt_id]

            wav_id = value[0]
            start = 0
            end = -1

            if len(value) > 1 and value[1] is not None:
                if value[1] == -1 or value[1] == '-1':
                    start = 0
                else:
                    start = value[1]

            if len(value) > 2 and value[2] is not None:
                end = value[2]

            f.write('{} {} {} {}\n'.format(utt_id, wav_id, start, end))

        f.close()
