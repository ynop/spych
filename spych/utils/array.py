import collections
import math

import numpy as np


def splice_features(features, splice_size=0, splice_step=1, repeat_border_frames=True):
    """
    Splice features in a array. Splicing extends a single feature with right and left context features.

    :param features: A 2D np-array with the shape (nr_of_features x feature_dimension).
    :param splice_size: Number of context features to use on the right and left. (splice_size = 4 --> resulting feature sizes = 9 * initial featdim)
    :param splice_step: Number of features to move for the next splice.
    :param repeat_border_frames: At the begin and end of the feature series the feature matrix has to be padded for splicing. If True it pads with the first/last feature otherwise with zeroes.
    :return: A 2D np-array with the spliced features.
    """
    num_features = np.size(features, 0)
    feature_size = np.size(features, 1)

    num_splices = math.ceil(num_features / splice_step)
    spliced_feature_size = ((splice_size * 2) + 1) * feature_size

    if repeat_border_frames:
        padded_matrix = np.pad(features, ((splice_size, splice_size), (0, 0)), 'edge')
    else:
        padded_matrix = np.pad(features, ((splice_size, splice_size), (0, 0)), 'constant', constant_values=0)

    new_shape = (num_splices, spliced_feature_size)
    new_strides = (padded_matrix.strides[0] * splice_step, padded_matrix.strides[1])

    return np.lib.stride_tricks.as_strided(padded_matrix, shape=new_shape, strides=new_strides)


def unsplice_features(features, splice_size=0, splice_step=1):
    """
    Take a array of spliced features and unsplice them. Uses the averaged values for a single feature.

    :param features: A 2D np-array with the spliced features.
    :param splice_size: Number of right and left context features that were used for splicing.
    :param splice_step: Step that was used for splicing.
    :return: A 2D np-array with the unspliced features.
    """
    num_spliced_features = np.size(features, 0)
    feat_per_feat = splice_size * 2 + 1
    feature_size = int(np.size(features, 1) / feat_per_feat)
    num_features = num_spliced_features * splice_step

    grouped_features = [[] for __ in range(num_features)]

    for i in range(num_spliced_features):
        unspliced_index = i * splice_step
        split_features = np.split(features[i], feat_per_feat)

        for j in range(feat_per_feat):
            target_feat_index = unspliced_index + j - splice_size
            if target_feat_index >= 0 and target_feat_index < num_features:
                grouped_features[target_feat_index].append(split_features[j])

    averaged_features = [np.average(x, 0) for x in grouped_features]

    return np.concatenate(averaged_features).reshape(-1, feature_size)
