from spych.dataset.io import kaldi
from spych.dataset.io import legacy
from spych.dataset.io import spych
from spych.dataset.io import tuda


def available_loaders():
    """ Return dictionary with the mapping loader-name, loader-class for all available dataset loaders. """
    return {
        spych.SpychDatasetLoader.type(): spych.SpychDatasetLoader,
        legacy.LegacySpychDatasetLoader.type(): legacy.LegacySpychDatasetLoader,
        kaldi.KaldiDatasetLoader.type(): kaldi.KaldiDatasetLoader,
        tuda.TudaDatasetLoader.type(): tuda.TudaDatasetLoader
    }


def create_loader_of_type(type_name):
    """ Return an instance of the loader of the given type. """
    loaders = available_loaders()

    if type_name in loaders.keys():
        return loaders[type_name]()
