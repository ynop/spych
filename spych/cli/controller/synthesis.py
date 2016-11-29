from cement.core import controller

from spych import synthesis


class SynthesisController(controller.CementBaseController):
    class Meta:
        label = 'synthesize'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Synthesize speech."

        arguments = [
            (['sentence_corpus_file'], dict(action='store', help='Path to file with sentences.')),
            (['config'], dict(action='store', help='Path to json configuration file.')),
            (['target_folder'], dict(action='store', help='Folder to store the created datasets.')),
            (['--clean-sentence-corpus-file'], dict(action='store', help='Path to file with cleaned sentences.'))
        ]

    @controller.expose(hide=True)
    def default(self):
        synthesis.synthesize_sentence_corpus_and_create_datasets_with_configs(self.app.pargs.sentence_corpus_file,
                                                                              self.app.pargs.config,
                                                                              self.app.pargs.target_folder,
                                                                              corpus_clean_path=self.app.pargs.clean_sentence_corpus_file)

        print('Done')

