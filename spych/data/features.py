import os
import glob

import numpy as np


class FeatureContainer(object):
    """
    This class defines a container for storing features (of a given type) of all utterances.
    """

    def __init__(self, path, dataset=None):
        self.path = path
        self.dataset = dataset

    def load_features_of_utterance(self, utterance_idx):
        """ Return the features for the given utterance as numpy array. None if the given utterance has no features."""
        feature_file_path = os.path.join(self.path, '{}.npy'.format(utterance_idx))
        return np.load(feature_file_path)

    def add_features_for_utterance(self, utterance_idx, features):
        """ Stores the given features (numpy array) for the given utterance. """

        feature_file_path = os.path.join(self.path, utterance_idx)
        np.save(feature_file_path, features)

    def feature_size(self):
        """ Return the feature dimension. Just reads a random utterance to get the feature size. """
        file = glob.glob(os.path.join(self.path, '*.npy'))[0]

        matrix = np.load(file)
        return np.size(matrix, 1)

    def get_statistics(self):
        """ Return basic stats for the features. Return min,max,mean,meanstdev. """
        per_utt_mins = []
        per_utt_maxs = []
        per_utt_means = []
        per_utt_stdevs = []

        for utterance_idx in self.dataset.utterances.keys():
            matrix = self.load_features_of_utterance(utterance_idx)

            if matrix is not None:
                per_utt_mins.append(np.min(matrix))
                per_utt_maxs.append(np.max(matrix))
                per_utt_means.append(np.mean(matrix))
                per_utt_stdevs.append(np.std(matrix))

        min = np.min(per_utt_mins)
        max = np.max(per_utt_maxs)
        mean = np.mean(per_utt_means)
        stdev = np.mean(per_utt_stdevs)

        return min, max, mean, stdev
