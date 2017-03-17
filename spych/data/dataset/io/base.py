import os
import shutil

from spych.data import dataset


class DatasetLoader(object):
    """
    A dataset loader is responsible to load a dataset from a filesystem or save a dataset to the filesystem.
    """

    def __init__(self, main_features=None):
        self.main_features = main_features

    @classmethod
    def type(cls):
        """ Return the dataset type (e.g. tuda, spych, TIMIT) of this loader. """
        return 'None'

    def check_for_missing_files(self, path):
        """ Return a list of necessary files for the current type of dataset that are missing in the given folder. None if path seems valid. """
        return None

    def load(self, path):
        """ Load a dataset from the given path. Creates empty dataset and calls subclass loader. """

        missing_files = self.check_for_missing_files(path)

        if missing_files is not None:
            raise IOError('Invalid dataset of type {}: files {} not found at {}'.format(self.type(), ' '.join(missing_files), path))

        loading_dataset = dataset.Dataset(path, loader=self)

        self._load(loading_dataset)

        return loading_dataset

    def _load(self, dataset):
        """ Effectively loads the dataset. Override in subclass. """
        raise NotImplementedError('Loader {} does not support loading datasets.'.format(self.type()))

    def save(self, dataset, path, copy_files=False):
        """ Saves the dataset at the given path. Override in subclass. """
        if os.path.isfile(path):
            raise ValueError('Target path {} is a file.'.format(path))

        if not os.path.exists(path):
            os.makedirs(path)

        if copy_files and dataset.path != path:
            files = self._copy_wavs(dataset, path)
        else:
            if dataset.path is None:
                base_path = os.getcwd()
            else:
                base_path = dataset.path

            files = {file.idx: os.path.relpath(file.path, base_path) for file in dataset.files.values()}

        self._save(dataset, path, files, copy_files=copy_files)

    def _save(self, dataset, path, files, copy_files=False):
        """ Effectively saves the dataset. Override in subclass. """
        raise NotImplementedError('Loader {} does not support saving datasets.'.format(self.type()))

    def _copy_wavs(self, dataset, path):
        new_files = {}

        for file_idx, file in dataset.files.items():
            source_path = file.path
            target_folder = os.path.abspath(os.path.join(path, 'audio_files'))
            target_path = os.path.join(target_folder, os.path.basename(file.path))
            rel_path = os.path.relpath(target_path, path)

            if not os.path.exists(target_folder):
                os.makedirs(target_folder)

            shutil.copy(source_path, target_path)

            new_files[file_idx] = rel_path

        return new_files
