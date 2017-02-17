class DatasetLoader(object):
    """
    A dataset loader is responsible to load a dataset from a filesystem or save a dataset to the filesystem.
    """

    def type(self):
        """ Returns the dataset type (e.g. tuda, spych, TIMIT) of this loader. """
        return 'None'

    def load(self, path):
        """ Loads a dataset from the given path. """
        pass

    def save(self, dataset, path):
        """ Saves the dataset at the given path. """
        pass
