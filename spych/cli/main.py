from cement.core import foundation

from spych.cli.controller import base
from spych.cli.controller import dataset

class SpychApp(foundation.CementApp):
    class Meta:
        label = 'spych'
        handlers = [
            base.BaseController,
            dataset.DatasetController
        ]

        extensions = ['mustache']

        # Internal templates (ship with application code)
        template_module = 'spych.ncli.templates'

        # default output handler
        output_handler = 'mustache'


def run():
    with SpychApp() as app:
        app.run()


if __name__ == "__main__":
    run()
