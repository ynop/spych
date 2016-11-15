from spych.data import dataset
from spych.data import dataset_validation


class DatasetFixer(object):
    def __init__(self, data, validation=None):
        self.data = data
        self.validation = validation

    def run_validation(self):
        if self.validation is None:
            self.validation = dataset_validation.DatasetValidation(self.data)
            self.validation.run_all_checks()

    def fix(self):
        self.delete_wavs_with_missing_files()
        self.delete_wavs_with_wrong_format()
        self.delete_utterances_with_missing_wav()

    def delete_wavs_with_missing_files(self):
        self.run_validation()

        self.data.remove_wavs(self.validation.missing_wavs, remove_files=False)
        self.data.save()

    def delete_wavs_with_wrong_format(self):
        self.run_validation()

        self.data.remove_wavs(self.validation.wavs_with_wrong_format, remove_files=True)
        self.data.save()

    def delete_utterances_with_missing_wav(self):
        self.run_validation()

        self.data.remove_utterances(self.validation.utterances_with_missing_wav_id)
        self.data.save()