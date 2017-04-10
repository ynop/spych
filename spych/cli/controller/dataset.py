import os

from cement.core import controller

from spych.data import dataset
from spych.data import segmentation
from spych.data.dataset import io


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
                                  help='Show detailed info or validation results.')),
        ]

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

    @controller.expose(help="Print information for a dataset.")
    def info(self):
        dset = dataset.Dataset.load(self.app.pargs.path, loader=self.app.pargs.format)

        feature_stats = []

        if self.app.pargs.detailed:
            for feature_name, feature_container in dset.features.items():
                stats = feature_container.get_statistics()
                feature_stats.append({
                    "name": feature_name,
                    "min": stats[0],
                    "max": stats[1],
                    "mean": stats[2],
                    "var": stats[3],
                    "stdv": stats[4],
                    "dim": feature_container.feature_size()
                })

        info_data = {
            "name": dset.name,
            "path": os.path.abspath(dset.path),
            "num_utterances": dset.num_utterances,
            "num_files": dset.num_files,
            "num_speakers": dset.num_speakers,
            "features": ', '.join(dset.features.keys()),
            "segmentations": ', '.join(dset.all_segmentation_keys),
            "subviews": ', '.join(dset.subviews.keys()),
            "feature_stats": feature_stats
        }

        self.app.render(info_data, 'dataset_info.mustache')

    @controller.expose(help="Create an empty dataset.")
    def new(self):
        ds_loader = io.create_loader_of_type(self.app.pargs.format)
        dset = dataset.Dataset(self.app.pargs.path, loader=ds_loader)
        dset.save()

    @controller.expose(help="Validate a dataset.")
    def validate(self):
        dset = dataset.Dataset.load(self.app.pargs.path, loader=self.app.pargs.format)
        validator = dataset.Validator.full_validator()

        result = validator.validate(dset)

        info_data = {
            "name": dset.name
        }

        for metric in dataset.ValidationMetric:
            if metric in [dataset.ValidationMetric.FEATURE_MISSING, dataset.ValidationMetric.SEGMENTATION_MISSING]:
                num_per_key = []

                for k, v in result[metric].items():
                    num_per_key.append('{} : {}'.format(k, len(v)))

                info_data['num_{}'.format(metric.value)] = ', '.join(num_per_key)
            else:
                info_data['num_{}'.format(metric.value)] = len(result[metric])

        if self.app.pargs.detailed:
            info_data["details"] = True

            for metric in dataset.ValidationMetric:
                if metric in [dataset.ValidationMetric.FEATURE_MISSING, dataset.ValidationMetric.SEGMENTATION_MISSING]:
                    values_per_feat = []

                    for k, v in result[metric].items():
                        if len(v) > 0:
                            values_per_feat.append('{} : {}'.format(k, ', '.join([str(x) for x in v])))

                    info_data[metric.value] = values_per_feat
                else:
                    info_data[metric.value] = result[metric]

        self.app.render(info_data, 'dataset_validation.mustache')

    @controller.expose(help="Rectify a dataset. (Remove missing, wrong format, empty files and utterances without file.")
    def rectify(self):
        dset = dataset.Dataset.load(self.app.pargs.path, loader=self.app.pargs.format)

        rectifier = dataset.Rectifier.full_rectifier()
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
            (['--main-features'], dict(action='store', help='Set the name of the main features (used when export to kaldi).')),
            (['--copy-files'], dict(action='store_true', help='Also copy the audio files to the target dataset.')),
        ]

    @controller.expose(hide=True)
    def default(self):
        source_loader = io.create_loader_of_type(self.app.pargs.source_format)
        target_loader = io.create_loader_of_type(self.app.pargs.target_format)

        source_loader.main_features = self.app.pargs.main_features
        target_loader.main_features = self.app.pargs.main_features

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


class ImportController(controller.CementBaseController):
    class Meta:
        label = 'dataset-import'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Import data to the dataset (features)."

        arguments = [
            (['path'], dict(action='store', help='Path to the dataset to import data into.')),
            (['-f', '--format'], format_argument()),
            (['--scp'], dict(action='store', help='Path to an kaldi scp file (for importing features).')),
            (['--feat-container'], dict(action='store', help='Name of the feature container to import features into.')),
            (['--segmentation-key'], dict(action='store', help='Name for the segmentation to import')),
            (['--ctm'], dict(action='store', help='Path to a ctm file to import as segmentation.')),
            (['--audacity'], dict(action='store', help='Path to a audacity file to import as segmentation.')),
            (['--utterance-id'], dict(action='store', help='Utterance id (When importing audacity label file).'))
        ]

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

    @controller.expose(help="Import features.")
    def features(self):
        feat_container_name = self.app.pargs.feat_container

        if feat_container_name is None:
            print('A feature container (name) has to be specified to import features into.')
            return

        dset = dataset.Dataset.load(self.app.pargs.path, loader=self.app.pargs.format)

        if feat_container_name not in dset.features.keys():
            dset.add_new_feature_container(feat_container_name, 'features_{}'.format(feat_container_name))

        for index, (utterance_idx, feature_matrix) in enumerate(io.KaldiDatasetLoader.feature_scp_generator(self.app.pargs.scp)):
            dset.add_features(utterance_idx, feature_matrix, feat_container_name)

        dset.save()

        print('Imported {} feature-matrices into the dataset with {} utterances.'.format(index + 1, dset.num_utterances))

    @controller.expose(help="Import segmentations.")
    def segmentation(self):
        if self.app.pargs.segmentation_key is None:
            print('You have to provide a segmentation key.')
            return

        if self.app.pargs.ctm is None and self.app.pargs.audacity is None:
            print('You have to provide a segmentation file (--ctm, --audacity).')
            return

        dset = dataset.Dataset.load(self.app.pargs.path, loader=self.app.pargs.format)

        count = 0

        if self.app.pargs.ctm is not None:
            segs = segmentation.Segmentation.from_ctm(self.app.pargs.ctm)

            for seg in segs:
                if seg.utterance_idx in dset.utterances.keys():
                    seg.key = self.app.pargs.segmentation_key
                    dset.import_segmentation(seg)
                    count += 1
        elif self.app.pargs.audacity is not None:
            if self.app.pargs.utterance_id is None:
                print('You have to provide an utterance-id to import the audacity labels to.')
            else:
                seg = segmentation.Segmentation.from_audacity(self.app.pargs.audacity)
                seg.key = self.app.pargs.segmentation_key
                seg.utterance_idx = self.app.pargs.utterance_id
                dset.import_segmentation(seg)
                count += 1

        dset.save()

        print('Imported {} segmentations with key: {}'.format(count, self.app.pargs.name))


class ModifyController(controller.CementBaseController):
    class Meta:
        label = 'dataset-modify'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Apply different modifications to a dataset."

        arguments = [
            (['path'], dict(action='store', help='Path to the dataset to import data into.')),
            (['-f', '--format'], format_argument()),
            (['--file-path'], dict(action='store', help='Path to set for files in the dataset.'))
        ]

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

    @controller.expose(help="Set the path of all files to the path given with the --file-path option.")
    def set_file_path(self):
        if self.app.pargs.file_path is None:
            print("You have to provide a path (--file-path).")
            return

        dset = dataset.Dataset.load(self.app.pargs.path, loader=self.app.pargs.format)

        dset.set_relative_wav_paths(self.app.pargs.file_path)
