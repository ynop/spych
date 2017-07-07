from torch.utils import data


class SpychDataset(data.Dataset):
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
