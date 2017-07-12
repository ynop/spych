import collections

import numpy as np

import torch
from torch.utils import data
from torch.utils.data import dataloader

string_classes = (str, bytes)


# custom collate to cat frames of different sized utterances together -> cat instead stack
def _custom_collate(batch):
    if isinstance(batch[0], collections.Mapping):
        return {key: _custom_collate([d[key] for d in batch]) for key in batch[0]}
    elif isinstance(batch[0], collections.Sequence):
        transposed = zip(*batch)
        return [_custom_collate(samples) for samples in transposed]
    else:
        return dataloader.default_collate(batch)


# custom collate to pad utterances to the biggest
def _utterance_pad_collate(batch):
    """
    input: batch_size * nr_feats_per_batch * np.array(utt_len * frame_dimension)
    output: nr_feats_per_batch * (utt_lengths, tensor(batch_size * max_len * frame_dimension))
    """
    sorted_samples = sorted(batch, key=lambda x: np.size(x[0], 0), reverse=True)

    parts = []

    for batch_part in zip(*sorted_samples):
        lengths = [np.size(x, 0) for x in batch_part]
        max_length = max(lengths)

        padded_utts = [np.pad(utt, ((0, max_length - np.size(utt, 0)), (0, 0)), 'constant') for utt in batch_part]

        data = dataloader.default_collate(padded_utts)

        parts.append((lengths, data))

    return parts


def frame_batch_loader(dataset, batch_size=1, shuffle=False, num_workers=0, pin_memory=False, drop_last=False):
    """
    Returns a dataloader which generates batches with concatenated frame from [batch_size] utterances.
    """
    return dataloader.DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers, collate_fn=_custom_collate,
                                 pin_memory=pin_memory, drop_last=drop_last)


def padded_utterance_batch_loader(dataset, batch_size=1, shuffle=False, num_workers=0, pin_memory=False, drop_last=False):
    """
    Returns a dataloader which generates batches with [batch_size] utterances padded to the same length. (batch_size x max_utt_len x frame_dimension)
    """
    return dataloader.DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers, collate_fn=_utterance_pad_collate,
                                 pin_memory=pin_memory, drop_last=drop_last)


class Dataset(data.Dataset):
    """
    Dataset that provides utterance features. It can use multiple Spych datasets (spych.data.dataset.Dataset) as backend.

    This dataset contains samples for every utterance that is available in all base datasets.

    Arguments:
        base_datasets: list of tuples (dataset, feature-name, feature-pipeline)
    """

    def __init__(self, base_datasets=[]):
        self.base_datasets = base_datasets
        self.feature_containers = []

        self.utterance_ids = self._get_utterances_contained_in_all_datasets()

    def _get_utterances_contained_in_all_datasets(self):
        common = set(self.base_datasets[0][0].utterances.keys())

        for i in range(1, len(self.base_datasets)):
            ds = self.base_datasets[i][0]
            common = common.intersection(ds.utterances.keys())

        return list(common)

    def open(self):
        self.feature_containers = []

        for item in self.base_datasets:
            dataset = item[0]
            fc_name = item[1]

            fc = dataset.features[fc_name]
            fc.open()

            fpipe = None

            if len(item) > 2:
                fpipe = item[2]

            self.feature_containers.append((fc, fpipe))

    def close(self):
        for fc in self.feature_containers:
            fc.close()

        self.feature_containers = []

    def __len__(self):
        return len(self.utterance_ids)

    def __getitem__(self, item):
        utt_id = self.utterance_ids[item]

        output = []

        for fc, feat_pipe in self.feature_containers:
            if feat_pipe:
                output.append(feat_pipe.process(fc.get(utt_id)))
            else:
                output.append(fc.get(utt_id))

        return output
