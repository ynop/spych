from cement.core import foundation

from spych_cli.controller import base
from spych_cli.controller import dataset


class SpychApp(foundation.CementApp):
    class Meta:
        label = 'spych'
        handlers = [
            base.BaseController,
            dataset.DatasetController
        ]

        extensions = ['mustache']

        # Internal templates (ship with application code)
        template_module = 'spych_cli.templates'

        # default output handler
        output_handler = 'mustache'


with SpychApp() as app:
    app.run()
