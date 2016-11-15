from cement.core import controller

from spych.data import dataset
from spych.data import dataset_validation


class DatasetController(controller.CementBaseController):
    class Meta:
        label = 'dataset'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Working with datasets."

        arguments = [
            (['--path'],
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

    @controller.expose(help="Validate a dataset and print results.")
    def validate(self):
        dset = dataset.Dataset.load_from_path(self.app.pargs.path)

        validator = dataset_validation.DatasetValidation(dset)
        validator.run_all_checks()

        info_data = {
            "name": dset.name(),
            "missing_wavs": len(validator.missing_wavs),
            "wavs_with_wrong_format": len(validator.wavs_with_wrong_format),
            "wavs_without_utterances": len(validator.wavs_without_utterances),
            "utterances_with_missing_wav_id": len(validator.utterances_with_missing_wav_id),
            "missing_empty_transcriptions": len(validator.missing_empty_transcriptions),
            "missing_empty_speakers": len(validator.missing_empty_speakers),
            "missing_empty_genders": len(validator.missing_empty_genders),
            "invalid_utt_ids_in_utt2spk": len(validator.invalid_utt_ids_in_utt2spk)
        }

        self.app.render(info_data, 'dataset_validation.mustache')
