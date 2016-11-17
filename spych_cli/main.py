from cement.core import foundation

from spych_cli.controller import base
from spych_cli.controller import dataset
from spych_cli.controller import synthesis
from spych_cli.controller import lexicon

class SpychApp(foundation.CementApp):
    class Meta:
        label = 'spych'
        handlers = [
            base.BaseController,
            dataset.DatasetController,
            dataset.DatasetValidationController,
            dataset.DatasetFixController,
            dataset.DatasetExportController,
            dataset.DatasetMergeController,
            lexicon.LexiconController,
            synthesis.SynthesisController
        ]

        extensions = ['mustache']

        # Internal templates (ship with application code)
        template_module = 'spych_cli.templates'

        # default output handler
        output_handler = 'mustache'


with SpychApp() as app:
    app.run()
