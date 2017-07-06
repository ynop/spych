import os


class KaldiData(object):
    def __init__(self, env):
        self.env = env

    def validate_data(self, data_folder):
        """
        Validates data folder
        :param data_folder: path
        :return:
        """

        self.env.run_bash_script('utils/validate_data_dir.sh', args=[os.path.abspath(data_folder)])

    def fix_data(self, data_folder):
        """
        Fix data folder
        :param data_folder: path
        :return:
        """
        self.env.run_bash_script('utils/fix_data_dir.sh', args=[os.path.abspath(data_folder)])
