import os

from spych.synthesis import synthesizer
from spych.synthesis import mary
from spych.utils import jsonfile


def synthesize_sentence_corpus_and_create_datasets_with_configs(corpus_path, config_path, target_folder, corpus_clean_path=None):
    """
    Synthesizes the given corpus for all given configurations and creates datasets from it.

    Configuration file (json):
    [
        {
           "dataset_name" : [dataset-name],
           "locale" : [locale],
           "voice": [voice_id],
           "effects": {
                        [effect-name]: [effect-value],
                        ...
                        }
        },
        ...
    ]

    :param corpus_path: Path to sentence corpus.
    :param config_path: Path to file with configurations
    :param target_folder: Path to store the datasets
    """

    configurations = jsonfile.read_json_file(config_path)

    for config in configurations:
        print('Synthesize {} ...'.format(config['dataset_name']))

        dataset_path = os.path.join(target_folder, config['dataset_name'])
        synthesizer_config = synthesizer.SynthesizerConfig(locale=config['locale'], voice=config['voice'], effects=config['effects'])
        synthesizer_instance = mary.MarySynthesizer(config=synthesizer_config)

        synthesizer_instance.synthesize_sentence_corpus_and_create_dataset(corpus_path, dataset_path, corpus_clean_path=corpus_clean_path)
