import random

import numpy as np

from spych.utils import array


class BatchGenerator(object):
    """
    Class that provides functions to generate batches from a single or multiple datasets.
    If multiple datasets only utterances are considered, that exist in all of the given datasets.
    """

    def __init__(self, datasets):
        if type(datasets) == list:
            self.datasets = datasets
        else:
            self.datasets = [datasets]
        self.common_utterance_ids = []

        self._get_utterances_contained_in_all_datasets()

    def generate_utterance_batches(self, batch_size):
        """ Return a generator which yields batches. One batch is a list of utterance-ids of size batch-size. """

        shuffled_utt_ids = self._get_shuffled_utterance_ids()

        for i in range(0, len(shuffled_utt_ids), batch_size):
            yield shuffled_utt_ids[i:i + batch_size]

    def generate_feature_batches(self, feature_name, batch_size, splice_sizes=0, splice_step=1, repeat_border_frames=True):
        """
        Return a generator which yields batchs. One batch contains the concatenated features of batch_size utterances.
        Yields list with length equal to the number of datasets in this generator. The list contains ndarrays with the concatenated features.

        :param feature_name: Name of the feature container in the dataset to use.
        :param batch_size: Number of utterances in one batch
        :param splice_sizes: Appends x previous and next features to the sample. (e.g. if splice_size is 4 the sample contains 9 features in total).
        If a list of ints is given the different splice-sizes for the different datasets are used.
        :param splice_step: Number of features to move forward for the next sample.
        :param repeat_border_frames: If True repeat the first and last frame for splicing. Otherwise pad with zeroes.
        :returns: generator
        """

        if type(splice_sizes) == int:
            splice_sizes *= len(self.datasets) * [splice_sizes]

        for batch_utt_ids in self.generate_utterance_batches(batch_size):

            batch_features = [[] for __ in self.datasets]

            for utt_id in batch_utt_ids:

                # get the features of all datasets
                per_set_features = [x.features[feature_name].load_features_of_utterance(utt_id) for x in self.datasets]

                # clip features to the number of the smallest feature matrix
                per_set_feature_lengths = [np.size(x, 0) for x in per_set_features]
                min_feature_length = min(per_set_feature_lengths)

                # clip and splice the features and add to the batch
                for index, features in enumerate(per_set_features):
                    features = features[:min_feature_length]
                    features = array.splice_features(features, splice_sizes[index], splice_step, repeat_border_frames)
                    batch_features[index].append(features)

            batch = [np.concatenate(x) for x in batch_features]

            yield batch

    def _get_utterances_contained_in_all_datasets(self):
        common = set(self.datasets[0].utterances.keys())

        for ds in self.datasets:
            common = common.intersection(ds.utterances.keys())

        self.common_utterance_ids = common

    def _get_shuffled_utterance_ids(self):
        utterances = list(self.common_utterance_ids)
        random.shuffle(utterances)

        return utterances
