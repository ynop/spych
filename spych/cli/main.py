from cement.core import foundation

from spych.cli.controller import base
from spych.cli.controller import dataset
from spych.cli.controller import wav
from spych.cli.controller import lexicon


class SpychApp(foundation.CementApp):
    class Meta:
        label = 'spych'
        handlers = [
            base.BaseController,
            dataset.MainController,
            dataset.CopyController,
            dataset.MergeController,
            dataset.ImportController,
            dataset.ModifyController,
            wav.MainController,
            wav.AddNoiseController,
            wav.SNREstimationController,
            wav.SegmentExtractionController,
            lexicon.MainController
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
