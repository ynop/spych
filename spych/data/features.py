import h5py

import numpy as np


class FeatureContainer(object):
    """
    This class defines a container for storing features (of a given type) of all utterances.
    """

    def __init__(self, path):
        self.path = path
        self.file = None

    def open(self):
        if self.file is None:
            self.file = h5py.File(self.path, 'a')

    def close(self):
        if self.file is not None:
            self.file.close()
            self.file = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def add(self, utterance_idx, features):
        if utterance_idx in self.file:
            del self.file[utterance_idx]

        self.file.create_dataset(utterance_idx, data=features, compression="lzf")

    def remove(self, utterance_idx):
        if utterance_idx in self.file:
            del self.file[utterance_idx]

    def get(self, utterance_idx):
        if utterance_idx in self.file:
            return self.file[utterance_idx][()]
        else:
            return None

    def feature_size(self):
        return list(self.file.items())[0][1].shape[1]

    def get_statistics(self):
        """ Return basic stats for the features. Return min,max,mean,meanstdev. """
        per_utt_mins = []
        per_utt_maxs = []
        per_utt_means = []
        per_utt_vars = []
        per_utt_stdevs = []

        for utt_id, matrix in self.file.items():
            per_utt_mins.append(np.min(matrix))
            per_utt_maxs.append(np.max(matrix))
            per_utt_means.append(np.mean(matrix))
            per_utt_vars.append(np.var(matrix))
            per_utt_stdevs.append(np.std(matrix))

        min = np.min(per_utt_mins)
        max = np.max(per_utt_maxs)
        mean = np.mean(per_utt_means)
        var = np.mean(per_utt_vars)
        stdev = np.mean(per_utt_stdevs)

        return min, max, mean, var, stdev
