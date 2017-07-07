from torch.utils import data


class SpychDataset(data.Dataset):
    def __init__(self, base_datasets=[], feature_pipeline=None):
        self.base_datasets = base_datasets
        self.feature_containers = []
        self.feature_pipeline = feature_pipeline

        self.utterance_ids = self._get_utterances_contained_in_all_datasets()

    def _get_utterances_contained_in_all_datasets(self):
        common = set(self.base_datasets[0][0].utterances.keys())

        for i in range(1, len(self.base_datasets)):
            ds = self.base_datasets[i][0]
            common = common.intersection(ds.utterances.keys())

        return common

    def open(self):
        self.feature_containers = []

        for dataset, fc_name in self.base_datasets:
            fc = dataset.features[fc_name]
            fc.open()
            self.feature_containers.append(fc)

    def close(self):
        for fc in self.feature_containers:
            fc.close()

        self.feature_containers = []

    def __len__(self):
        return len(self.utterance_ids)

    def __getitem__(self, item):
        utt_id = self.utterance_ids[item]

        if self.feature_pipeline is not None:
            return [self.feature_pipeline.process(fc.get(utt_id)) for fc in self.feature_containers]
        else:
            return [fc.get(utt_id) for fc in self.feature_containers]
