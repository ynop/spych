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

    def batches_with_utterance_idxs(self, batch_size):
        """ Return a generator which yields batches. One batch is a list of utterance-ids of size batch-size. """

        shuffled_utt_ids = self._get_shuffled_utterance_ids()

        for i in range(0, len(shuffled_utt_ids), batch_size):
            yield shuffled_utt_ids[i:i + batch_size]

    def batches_with_utterance_idx_and_features(self, feature_name, batch_size):
        """
        Return a generator which yields batches. One batch contains features from batch_size utterances.
        Yields a list of lists. Every sublist contains first the utterance id and following the feature arrays (ndarray) of all datasets.

        e.g. If there are two source datasets:

        [
            [utt_id, dataset_1_feature, dataset_2_feature],
            [utt_id2, dataset_1_feature2, dataset_2_feature2],
            ...
        ]

        :param feature_name: Name of the feature container in the dataset to use.
        :param batch_size: Number of utterances in one batch
        :return: generator
        """

        for batch_utt_ids in self.batches_with_utterance_idxs(batch_size):

            batch_features = []
            feature_containers = []

            for ds in self.datasets:
                fc = ds.features[feature_name]
                fc.open()
                feature_containers.append(fc)

            for utt_id in batch_utt_ids:
                per_set_features = [x.get(utt_id) for x in feature_containers]
                per_set_features.insert(0, utt_id)
                batch_features.append(per_set_features)

            for fc in feature_containers:
                fc.close()

            yield batch_features


    def batches_with_features(self, feature_name, batch_size):
        """
        Return a generator which yields batches. One batch contains concatenated features from batch_size utterances.

        :param feature_name: Name of the feature container in the dataset to use.
        :param batch_size: Number of utterances in one batch
        :return: generator
        """

        for batch_utt_ids in self.batches_with_utterance_idxs(batch_size):

            batch = []

            for index, ds in enumerate(self.datasets):
                if type(feature_name) == list:
                    in_feature = feature_name[index]
                else:
                    in_feature = feature_name

                with ds.features[in_feature] as fc:
                    per_utt_features = [fc.get(x) for x in batch_utt_ids]

                ds_features = np.concatenate(per_utt_features)
                batch.append(ds_features)

            yield batch

    def batches_with_spliced_features(self, feature_name, batch_size, splice_sizes=0, splice_step=1, repeat_border_frames=True):
        """
        Return a generator which yields batches. One batch contains the concatenated features of batch_size utterances.
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

        for batch_utt_ids in self.batches_with_utterance_idxs(batch_size):

            batch_features = [[] for __ in self.datasets]
            feature_containers = []

            for ds in self.datasets:
                fc = ds.features[feature_name]
                fc.open()
                feature_containers.append(fc)

            for utt_id in batch_utt_ids:

                # get the features of all datasets
                per_set_features = [x.get(utt_id) for x in feature_containers]

                # clip features to the number of the smallest feature matrix
                per_set_feature_lengths = [np.size(x, 0) for x in per_set_features]
                min_feature_length = min(per_set_feature_lengths)

                # clip and splice the features and add to the batch
                for index, features in enumerate(per_set_features):
                    features = features[:min_feature_length]
                    features = array.splice_features(features, splice_sizes[index], splice_step, repeat_border_frames)
                    batch_features[index].append(features)

            for fc in feature_containers:
                fc.close()

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
