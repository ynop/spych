import os

import numpy as np


class FeatureContainer(object):
    """
    This class defines a container for storing features (of a given type) of all utterances.

    files : utterance-id --> feature-file-name
    """

    def __init__(self, path):
        self.files = {}
        self.path = path

    def load_features_of_utterance(self, utterance_idx):
        """ Return the features for the given utterance as numpy array. None if the given utterance has no features."""
        if utterance_idx in self.files.keys():
            return np.load(self.files[utterance_idx])

    def add_features_for_utterance(self, utterance_idx, features):
        """ Stores the given features (numpy array) for the given utterance. """

        feature_file_path = os.path.join(self.path, utterance_idx)
        np.save(feature_file_path, features)
