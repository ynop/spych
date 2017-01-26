from cement.core import foundation

from spych.cli.controller import base
from spych.cli.controller import dataset
from spych.cli.controller import synthesis
from spych.cli.controller import lexicon
from spych.cli.controller import scoring
from spych.cli.controller import wav


class SpychApp(foundation.CementApp):
    class Meta:
        label = 'spych'
        handlers = [
            base.BaseController,
            dataset.DatasetController,
            dataset.DatasetValidationController,
            dataset.DatasetFixController,
            dataset.DatasetExportController,
            dataset.DatasetImportController,
            dataset.DatasetMergeController,
            dataset.DatasetSubsetController,
            dataset.DatasetSplitController,
            dataset.DatasetShowController,
            dataset.DatasetModifyController,
            lexicon.LexiconController,
            synthesis.SynthesisController,
            scoring.ScoreController,
            wav.WavController,
            wav.SNRController
        ]

        extensions = ['mustache']

        # Internal templates (ship with application code)
        template_module = 'spych.cli.templates'

        # default output handler
        output_handler = 'mustache'


def run():
    with SpychApp() as app:
        app.run()


if __name__ == "__main__":
    run()
