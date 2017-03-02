import random


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

    def _get_utterances_contained_in_all_datasets(self):
        common = set(self.datasets[0].utterances.keys())

        for ds in self.datasets:
            common = common.intersection(ds.utterances.keys())

        self.common_utterance_ids = common

    def _get_shuffled_utterance_ids(self):
        utterances = list(self.common_utterance_ids)
        random.shuffle(utterances)

        return utterances

    def generate_batches_by_utterances(self, batch_size):
        """ Return a generator which yields batches. One batch is a list of utterance-ids of size batch-size. """

        shuffled_utt_ids = self._get_shuffled_utterance_ids()

        for i in range(0, len(shuffled_utt_ids), batch_size):
            yield shuffled_utt_ids[i:i + batch_size]
