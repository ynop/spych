from spych.dataset import dataset


class DatasetLoader(object):
    """
    A dataset loader is responsible to load a dataset from a filesystem or save a dataset to the filesystem.
    """

    def type(self):
        """ Return the dataset type (e.g. tuda, spych, TIMIT) of this loader. """
        return 'None'

    def check_for_missing_files(self, path):
        """ Return a list of necessary files for the current type of dataset that are missing in the given folder. None if path seems valid. """
        return None

    def load(self, path):
        """ Load a dataset from the given path. Creates empty dataset and calls subclass loader. """

        missing_files = self.check_for_missing_files(path)

        if missing_files is not None:
            raise IOError('Invalid dataset of type {}: files not found {}'.format(self.type(), ' '.join(missing_files)))

        loading_dataset = dataset.Dataset(path, loader=self)

        self._load(loading_dataset)

        return loading_dataset

    def _load(self, dataset):
        """ Effectively loads the dataset. Override in subclass. """
        raise NotImplementedError('Loader {} does not support loading datasets.'.format(self.type()))

    def save(self, dataset, path):
        """ Saves the dataset at the given path. Override in subclass. """
        raise NotImplementedError('Loader {} does not support saving datasets.'.format(self.type()))
