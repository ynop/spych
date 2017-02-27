import os

from cement.core import controller

from spych.dataset import dataset
from spych.dataset import io
from spych.dataset import validation
from spych.dataset import rectification


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
            (['-f', '--format'], format_argument()),
            (['--detailed'], dict(action='store_true',
                                  help='Show detailed validation results.')),
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

    @controller.expose(help="Validate a dataset.")
    def validate(self):
        dset = dataset.Dataset.load(self.app.pargs.path, loader=self.app.pargs.format)
        validator = validation.DatasetValidator.full_validator()

        result = validator.validate(dset)

        info_data = {
            "name": dset.name
        }

        for metric in validation.ValidationMetric:
            info_data['num_{}'.format(metric.value)] = len(result[metric])

        if self.app.pargs.detailed:
            info_data["details"] = True

            for metric in validation.ValidationMetric:
                info_data[metric.value] = result[metric]

        self.app.render(info_data, 'dataset_validation.mustache')

    @controller.expose(help="Rectify a dataset. (Remove missing, wrong format, empty files and utterances without file.")
    def rectify(self):
        dset = dataset.Dataset.load(self.app.pargs.path, loader=self.app.pargs.format)

        rectifier = rectification.DatasetRectifier.full_rectifier()
        rectifier.rectify(dset)

        dset.save()

    @controller.expose(help="Print all utterance-ids.")
    def print_utterance_ids(self):
        dset = dataset.Dataset.load(self.app.pargs.path, loader=self.app.pargs.format)
        print('\n'.join(dset.utterances.keys()))

    @controller.expose(help="Print all speaker-ids.")
    def print_speaker_ids(self):
        dset = dataset.Dataset.load(self.app.pargs.path, loader=self.app.pargs.format)
        print('\n'.join(dset.speakers.keys()))

    @controller.expose(help="Print all file-ids.")
    def print_file_ids(self):
        dset = dataset.Dataset.load(self.app.pargs.path, loader=self.app.pargs.format)
        print('\n'.join(dset.file.keys()))


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
            (['-v', '--subview'], dict(action='store',
                                       help='Only copy a specific subview.')),
            (['-s', '--source-format'], format_argument()),
            (['-t', '--target-format'], format_argument()),
            (['--copy-files'], dict(action='store_true', help='Also copy the audio files to the target dataset.')),
        ]

    @controller.expose(hide=True)
    def default(self):
        source_loader = io.create_loader_of_type(self.app.pargs.source_format)
        target_loader = io.create_loader_of_type(self.app.pargs.target_format)

        source_ds = source_loader.load(self.app.pargs.sourcepath)
        copy_ds = source_ds

        if self.app.pargs.subview is not None:
            copy_ds = source_ds.export_subview(self.app.pargs.subview)

        target_loader.save(copy_ds, self.app.pargs.targetpath, copy_files=self.app.pargs.copy_files)


class MergeController(controller.CementBaseController):
    class Meta:
        label = 'dataset-merge'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Merge a dataset into another."

        arguments = [
            (['targetpath'], dict(action='store', help='Path to the dataset to merge another into.')),
            (['mergepath'], dict(action='store', help='Path to the dataset to merge into the dataset at target path.')),
            (['-t', '--target-format'], format_argument()),
            (['-m', '--merge-format'], format_argument()),
            (['--copy-files'], dict(action='store_true', help='Also copy the audio files to the target dataset folder.'))
        ]

    @controller.expose(hide=True)
    def default(self):
        target_loader = io.create_loader_of_type(self.app.pargs.target_format)
        merge_loader = io.create_loader_of_type(self.app.pargs.merge_format)

        target_set = target_loader.load(self.app.pargs.targetpath)
        merge_set = merge_loader.load(self.app.pargs.mergepath)

        target_set.import_dataset(merge_set, copy_files=self.app.pargs.copy_files)
        target_set.save()
