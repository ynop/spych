from .kaldi import KaldiDatasetLoader
from .legacy import LegacySpychDatasetLoader
from .spych import SpychDatasetLoader
from .tuda import TudaDatasetLoader


def available_loaders():
    """ Return dictionary with the mapping loader-name, loader-class for all available dataset loaders. """
    return {
        SpychDatasetLoader.type(): SpychDatasetLoader,
        LegacySpychDatasetLoader.type(): LegacySpychDatasetLoader,
        KaldiDatasetLoader.type(): KaldiDatasetLoader,
        TudaDatasetLoader.type(): TudaDatasetLoader
    }


def create_loader_of_type(type_name):
    """ Return an instance of the loader of the given type. """
    loaders = available_loaders()

    if type_name in loaders.keys():
        return loaders[type_name]()
