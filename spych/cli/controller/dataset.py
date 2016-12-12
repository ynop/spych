from cement.core import controller

from spych.data import dataset
from spych.data import dataset_validation
from spych.data import dataset_fixing
from spych.data import dataset_split
from spych.utils import textfile
from spych.data.converter import kaldi


class DatasetController(controller.CementBaseController):
    class Meta:
        label = 'dataset'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Working with datasets."

        arguments = [
            (['path'],
             dict(action='store', help='path to dataset'))
        ]

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

    @controller.expose(help="Print information about a given dataset.")
    def info(self):
        dset = dataset.Dataset.load_from_path(self.app.pargs.path)

        info_data = {
            "name": dset.name(),
            "path": dset.path,
            "num_utterances": len(dset.utterances),
            "num_wavs": len(dset.wavs),
            "num_speakers": len(dset.all_speakers())
        }

        self.app.render(info_data, 'dataset_info.mustache')

    @controller.expose(help="Create an empty dataset.")
    def new(self):
        dset = dataset.Dataset(self.app.pargs.path)
        dset.save()


class DatasetMergeController(controller.CementBaseController):
    class Meta:
        label = 'merge'
        stacked_on = 'dataset'
        stacked_type = 'nested'
        description = "Merge two datasets."

        arguments = [
            (['path'], dict(action='store', help='path to target dataset')),
            (['merge_path'], dict(action='store', help='path to dataset to merge into target dataset')),
            (['--copy-wavs'], dict(action='store_true', help='Also copy the audio files to the target dataset folder.'))
        ]

    @controller.expose(hide=True)
    def default(self):
        target = dataset.Dataset.load_from_path(self.app.pargs.path)
        merge = dataset.Dataset.load_from_path(self.app.pargs.merge_path)
        target.merge_dataset(merge, copy_wavs=self.app.pargs.copy_wavs)
        target.save()


class DatasetSplitController(controller.CementBaseController):
    class Meta:
        label = 'split'
        stacked_on = 'dataset'
        stacked_type = 'nested'
        description = "Splits a dataset into multiple subsets."

        arguments = [
            (['path'], dict(action='store', help='path to dataset')),
            (['splits'], dict(action='store', nargs='+', help='Splits e.g. ../train=0.6 test=0.3 val=0.1')),
            (['--split-by'], dict(action='store', help='By which entity it should be splitted (utterance, speaker)', choices=['utterance', 'speaker'],
                                  default='utterance')),
            (['--copy-wavs'], dict(action='store_true', help='Also copy the audio files to the target dataset folder.')),
            (['--speaker-separated'],
             dict(action='store_true', help='Only has effect when splitted by utterances, makes sure one speaker only occurs in one subset.'))
        ]

    @controller.expose(hide=True)
    def default(self):
        target = dataset.Dataset.load_from_path(self.app.pargs.path)
        splitter = dataset_split.DatasetSplitter(target)

        if self.app.pargs.splits:
            config = {}

            for split in self.app.pargs.splits:
                parts = split.split('=')
                config[parts[0]] = float(parts[1])

            split_by_speaker = self.app.pargs.split_by == 'speaker'

            subsets = splitter.split(config, split_by_speakers=split_by_speaker, speaker_divided=self.app.pargs.speaker_separated,
                                     copy_wavs=self.app.pargs.copy_wavs)

            for subset in subsets:
                print("{} : {}".format(subset.name(), len(subset.utterances)))


class DatasetSubsetController(controller.CementBaseController):
    class Meta:
        label = 'subset'
        stacked_on = 'dataset'
        stacked_type = 'nested'
        description = "Create subset of a dataset. If no filter is given it just takes random items."

        arguments = [
            (['path'], dict(action='store', help='Path to the dataset, from which to create a subset.')),
            (['subset_path'], dict(action='store', help='Path to store the subset.')),
            (['--filter'], dict(action='store', help='(Only for speaker-id, utt-id) Filter to apply on the entity-id (Regex).')),
            (['--filter-list'], dict(action='store',
                                     help='(Only for transcriptions) Path to filter file. Only entities in the filter list are used. One line one entity (e.g. transcription)')),
            (['--count'], dict(action='store', help='Max number of items of the entity to use for the subset.')),
            (['--entity'], dict(action='store', help='Which entity to filter.', choices=['utterance-id', 'speaker-id', 'transcription'],
                                default='utterance-id')),
            (['--copy-wavs'], dict(action='store_true', help='Also copy the audio files to the subset folder.'))
        ]

    @controller.expose(hide=True)
    def default(self):
        source_dataset = dataset.Dataset.load_from_path(self.app.pargs.path)
        splitter = dataset_split.DatasetSplitter(source_dataset)

        subset_path = self.app.pargs.subset_path
        entity = self.app.pargs.entity
        filter_pattern = self.app.pargs.filter
        filter_list = self.app.pargs.filter_list
        filter_list_items = []
        count = self.app.pargs.count
        copy_wavs = self.app.pargs.copy_wavs
        subset = None

        try:
            if count is None:
                count = -1
            else:
                count = int(count)

        except ValueError:
            count = -1

        if filter_list is not None:
            if entity != 'transcription':
                print("--filter-list not supported for {}".format(entity))
                return
            else:
                for record in textfile.read_separated_lines_generator(filter_list, separator='\n', max_columns=1):
                    if len(record) > 0:
                        filter_list_items.append(record[0])

        if filter_pattern is not None:
            if entity not in ['speaker-id', 'utterance-id']:
                print("--filter not supported for {}".format(entity))
                return

        if entity == 'utterance-id':
            if filter_pattern is None:
                subset = splitter.create_subset_with_random_utterances(subset_path, count, copy_wavs=copy_wavs)
            else:
                subset = splitter.create_subset_with_filtered_utterances(subset_path, filter_pattern, max_items=count, copy_wavs=copy_wavs)

        elif entity == 'speaker-id':
            if filter_pattern is None:
                subset = splitter.create_subset_with_random_speakers(subset_path, count, copy_wavs=copy_wavs)
            else:
                subset = splitter.create_subset_with_filtered_speakers(subset_path, filter_pattern, max_items=count, copy_wavs=copy_wavs)

        elif entity == 'transcription':
            if filter_list is None:
                subset = splitter.create_subset_with_random_utterances(subset_path, count, copy_wavs=copy_wavs)
            else:
                subset = splitter.create_subset_with_filtered_transcriptions(subset_path, filter_list_items, count, copy_wavs=copy_wavs)

        else:
            print("unsupported entity {}".format(entity))
            return

        if subset is not None:
            info_data = {
                "name": subset.name(),
                "path": subset.path,
                "num_utterances": len(subset.utterances),
                "num_wavs": len(subset.wavs),
                "num_speakers": len(subset.all_speakers())
            }

        self.app.render(info_data, 'dataset_info.mustache')


class DatasetValidationController(controller.CementBaseController):
    class Meta:
        label = 'validate'
        stacked_on = 'dataset'
        stacked_type = 'nested'
        description = "Validate a dataset and print results."

        arguments = [
            (['path'], dict(action='store', help='path to dataset')),
            (['--details'], dict(action='store_true', help='Show details.'))
        ]

    @controller.expose(hide=True)
    def default(self):
        dset = dataset.Dataset.load_from_path(self.app.pargs.path)

        validator = dataset_validation.DatasetValidation(dset)
        validator.run_all_checks()

        info_data = {
            "name": dset.name(),
            "num_missing_wavs": len(validator.missing_wavs),
            "num_empty_wavs": len(validator.empty_wavs),
            "num_wavs_with_wrong_format": len(validator.wavs_with_wrong_format),
            "num_wavs_without_utterances": len(validator.wavs_without_utterances),
            "num_utterances_with_missing_wav_id": len(validator.utterances_with_missing_wav_id),
            "num_utterances_with_invalid_start_end": len(validator.utterances_with_invalid_start_end),
            "num_missing_empty_transcriptions": len(validator.missing_empty_transcriptions),
            "num_missing_empty_speakers": len(validator.missing_empty_speakers),
            "num_missing_empty_genders": len(validator.missing_empty_genders),
            "num_invalid_utt_ids_in_utt2spk": len(validator.invalid_utt_ids_in_utt2spk)
        }

        if self.app.pargs.details:
            info_data["details"] = True
            info_data["missing_wavs"] = validator.missing_wavs
            info_data["empty_wavs"] = validator.empty_wavs
            info_data["wavs_with_wrong_format"] = validator.wavs_with_wrong_format
            info_data["wavs_without_utterances"] = validator.wavs_without_utterances
            info_data["utterances_with_missing_wav_id"] = validator.utterances_with_missing_wav_id
            info_data["utterances_with_invalid_start_end"] = validator.utterances_with_invalid_start_end
            info_data["missing_empty_transcriptions"] = validator.missing_empty_transcriptions
            info_data["missing_empty_speakers"] = validator.missing_empty_speakers
            info_data["missing_empty_genders"] = validator.missing_empty_genders
            info_data["invalid_utt_ids_in_utt2spk"] = validator.invalid_utt_ids_in_utt2spk

        self.app.render(info_data, 'dataset_validation.mustache')


class DatasetFixController(controller.CementBaseController):
    class Meta:
        label = 'fix'
        stacked_on = 'dataset'
        stacked_type = 'nested'
        description = "Fix a dataset."

        arguments = [
            (['path'], dict(action='store', help='path to dataset'))
        ]

    @controller.expose(hide=True)
    def default(self):
        dset = dataset.Dataset.load_from_path(self.app.pargs.path)
        fixer = dataset_fixing.DatasetFixer(dset)

        fixer.fix()

        print('Done')


class DatasetExportController(controller.CementBaseController):
    class Meta:
        label = 'export'
        stacked_on = 'dataset'
        stacked_type = 'nested'
        description = "Export a dataset to another format."

        arguments = [
            (['path'], dict(action='store', help='path to dataset to export')),
            (['out'], dict(action='store', help='path to export the dataset to.')),
            (['format'], dict(action='store', help='format (kaldi)', choices=['kaldi'])),
            (['--copy-wavs'], dict(action='store_true', help='Also copy the audio files to the out folder.'))
        ]

    @controller.expose(hide=True)
    def default(self):
        dset = dataset.Dataset.load_from_path(self.app.pargs.path)

        target_path = self.app.pargs.out
        target_format = self.app.pargs.format

        if target_format == 'kaldi':
            print('Exporting:')
            print('From: {}'.format(dset.path))
            print('To: {}'.format(target_path))
            print('Format: {}'.format(target_format))

            exporter = kaldi.KaldiExporter(target_path, dset, copy_wavs=self.app.pargs.copy_wavs)
            exporter.run()

        else:
            print('Format {} not supported'.format(target_format))

        print('Done')


class DatasetImportController(controller.CementBaseController):
    class Meta:
        label = 'import'
        stacked_on = 'dataset'
        stacked_type = 'nested'
        description = "Import a dataset from another format to the spych format."

        arguments = [
            (['path'], dict(action='store', help='path to dataset to import the dataset to')),
            (['out'], dict(action='store', help='path to dataset to import')),
            (['format'], dict(action='store', help='format (kaldi)', choices=['kaldi'])),
            (['--copy-wavs'], dict(action='store_true', help='Also copy the audio files to the out folder.'))
        ]

    @controller.expose(hide=True)
    def default(self):
        source_path = self.app.pargs.out
        target_path = self.app.pargs.path
        source_format = self.app.pargs.format

        if source_format == 'kaldi':
            print('Importing:')
            print('Format: {}'.format(source_format))
            print('From: {}'.format(source_path))
            print('To: {}'.format(target_path))

            importer = kaldi.KaldiConverter(target_path, source_path, copy_wavs=self.app.pargs.copy_wavs)
            importer.run()
        else:
            print('Format {} not supported'.format(source_format))

        print('Done')
