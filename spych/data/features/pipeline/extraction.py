import numpy as np
import librosa

from . import base


class SpectrumExtractionStage(base.ExtractionStage):
    def __init__(self, win_length, win_step):
        self.win_length = win_length
        self.win_step = win_step

    def compute_raw(self, samples):
        return np.abs(librosa.stft(samples, n_fft=self.win_length, hop_length=self.win_step)) ** 2

    def extract(self, samples, sampling_rate):
        spec = self.compute_raw(samples)
        spec = spec.T.astype(np.float32)
        return spec


class MelFilterbankExtractionStage(SpectrumExtractionStage):
    def __init__(self, num_mel=23, win_length=400, win_step=160):
        super(MelFilterbankExtractionStage, self).__init__(win_length=win_length, win_step=win_step)

        self.num_mel = num_mel

    def compute_raw(self, samples, sampling_rate):
        spec = super(MelFilterbankExtractionStage, self).compute_raw(samples)
        mel_filter = librosa.filters.mel(sampling_rate, self.win_length, n_mels=self.num_mel)
        mel = np.dot(mel_filter, spec)

        return mel

    def extract(self, samples, sampling_rate):
        mel = self.compute_raw(samples, sampling_rate)
        mel = mel.T.astype(np.float32)

        return mel


class MFCCExtractionStage(MelFilterbankExtractionStage):
    def __init__(self, num_mfcc=13, num_mel=23, win_length=400, win_step=160):
        super(MFCCExtractionStage, self).__init__(num_mel=num_mel, win_length=win_length, win_step=win_step)

        self.num_mfcc = num_mfcc

    def compute_raw(self, samples, sampling_rate):
        mel = super(MFCCExtractionStage, self).compute_raw(samples, sampling_rate)
        mfcc = librosa.feature.mfcc(S=librosa.power_to_db(mel), n_mfcc=self.num_mfcc)

        return mfcc

    def extract(self, samples, sampling_rate):
        mfcc = self.compute_raw(samples, sampling_rate)
        mfcc = mfcc.T.astype(np.float32)

        return mfcc
