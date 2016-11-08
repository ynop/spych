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
        pass
