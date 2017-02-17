from spych.dataset import dataset


class DatasetLoader(object):
    """
    A dataset loader is responsible to load a dataset from a filesystem or save a dataset to the filesystem.
    """

    def type(self):
        """ Returns the dataset type (e.g. tuda, spych, TIMIT) of this loader. """
        return 'None'

    def load(self, path):
        """ Loads a dataset from the given path. Creates empty dataset and calls subclass loader. """
        loading_dataset = dataset.Dataset(path, loader_type=self)
        return self._load(loading_dataset)

    def _load(self, dataset):
        """ Effectively loads the dataset. Override in subclass. """
        raise NotImplementedError('Loader {} does not support loading datasets.'.format(self.type()))

    def save(self, dataset, path):
        """ Saves the dataset at the given path. Override in subclass. """
        raise NotImplementedError('Loader {} does not support saving datasets.'.format(self.type()))
