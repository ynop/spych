import librosa

from . import base


class MelToMFCCStage(base.ProcessingStage):
    def __init__(self, num_mfcc=13):
        self.num_mfcc = num_mfcc

    def process(self, feature_matrix):
        mel = librosa.power_to_db(feature_matrix.T)
        mfcc = librosa.feature.mfcc(S=mel, n_mfcc=13)
        return mfcc.T.astype('float32')
