import os

from spych.legacy.data import dataset
from spych.synthesis import synthesizer
from spych.synthesis import mary
from spych.utils import jsonfile


def synthesize_sentence_corpus_and_create_datasets_with_configs(corpus_path, config_path, target_folder, corpus_clean_path=None):
    """
    Synthesizes the given corpus for all given configurations and creates datasets from it.

    Configuration file (json):
    {
        "name" : "tract_scaler_diff",
        "locale" : "de",
        "voices" : [
            "bits3-hsmm"
        ],
        "effects" : {
            "TractScaler" : [
                {
                    "alias" : "",
                    "value" : [0.25, 4.0, 0.5],
                    "prefix" : "amount:",
                    "suffix" : ";"
                }
            ],
            "F0Scale" : [
                {
                    "alias" : "",
                    "value" : [0.0, 3.0, 1.5],
                    "prefix" : "f0Scale:",
                    "suffix" : ";"
                }
            ] ,
            "F0Add" : [
                {
                    "alias" : "",
                    "value" : 150.0,
                    "prefix" : "f0Add:",
                    "suffix" : ";"
                }
            ]
        }
    }

    :param corpus_path: Path to sentence corpus.
    :param config_path: Path to file with configurations
    :param target_folder: Path to store the datasets
    :param corpus_clean_path: Path to cleaned sentence corpus.
    """

    config = jsonfile.read_json_file(config_path)

    print('Synthesize {} ...'.format(config['name']))

    dataset_path = os.path.join(target_folder, config['name'])
    synthesizer_config = synthesizer.SynthesizerConfig(locale=config['locale'], voices=config['voices'], effects=config['effects'])
    synthesizer_instance = mary.MarySynthesizer(config=synthesizer_config)

    synthesizer_instance.synthesize_sentence_corpus_and_create_dataset(corpus_path, dataset_path, corpus_clean_path=corpus_clean_path)


def synthesize_dataset(source_path, target_path):
    source_dataset = dataset.Dataset.load_from_path(source_path)

    synthesizer_instance = mary.MarySynthesizer(config=None)
    synthesizer_instance.synthesize_dataset(source_dataset, target_path)
