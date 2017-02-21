import os

from cement.core import controller

from spych.dataset import dataset
from spych.dataset import io


class DatasetController(controller.CementBaseController):
    class Meta:
        label = 'dataset'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Working with audio datasets."

        arguments = [
            (['path'], dict(action='store',
                            help='Path to the dataset (Folder).')),
            (['--format'], dict(action='store',
                                help='Dataset format (spych [default], spych-legacy, kaldi, tuda)',
                                choices=['spych', 'spych-legacy', 'kaldi', 'tuda'],
                                default='spych')),
        ]

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

    @controller.expose(help="Print information for a dataset.")
    def info(self):
        dset = dataset.Dataset.load(self.app.pargs.path, loader=self.app.pargs.format)

        info_data = {
            "name": dset.name,
            "path": os.path.abspath(dset.path),
            "num_utterances": dset.num_utterances,
            "num_files": dset.num_files,
            "num_speakers": dset.num_speakers
        }

        self.app.render(info_data, 'dataset_info.mustache')

    @controller.expose(help="Create an empty dataset.")
    def new(self):
        loader = io.create_loader_of_type(self.app.pargs.format)
        dset = dataset.Dataset(self.app.pargs.path, loader=loader)
        dset.save()
