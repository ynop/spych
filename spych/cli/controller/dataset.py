import os

from cement.core import controller

from spych.dataset import dataset
from spych.dataset import io


def format_argument():
    return dict(action='store',
                help='Dataset format (spych [default], spych-legacy, kaldi, tuda)',
                choices=['spych', 'spych-legacy', 'kaldi', 'tuda'],
                default='spych')






class MainController(controller.CementBaseController):
    class Meta:
        label = 'dataset'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Working with audio datasets."

        arguments = [
            (['path'], dict(action='store',
                            help='Path to the dataset (Folder).')),
            (['--format'], format_argument()),
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


class CopyController(controller.CementBaseController):
    class Meta:
        label = 'dataset-copy'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Copy a dataset, convert from one format to another."

        arguments = [
            (['sourcepath'], dict(action='store',
                                  help='Path to the folder of the source dataset.')),
            (['targetpath'], dict(action='store',
                                  help='Path to the folder to copy the dataset to.')),
            (['-s', '--source-format'], format_argument()),
            (['-t', '--target-format'], format_argument()),
            (['--copy-files'], dict(action='store_true', help='Also copy the audio files to the target dataset.')),
        ]

    @controller.expose(hide=True)
    def default(self):
        source_loader = io.create_loader_of_type(self.app.pargs.source_format)
        target_loader = io.create_loader_of_type(self.app.pargs.target_format)

        source_ds = source_loader.load(self.app.pargs.sourcepath)
        target_loader.save(source_ds, self.app.pargs.targetpath)
