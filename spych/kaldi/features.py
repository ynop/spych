import os


class KaldiFeatures(object):

    def __init__(self, env):
        self.env = env

    def compute_cmvn_stats(self, data_folder, output_folder, log_folder, fake=False):
        args = [
            os.path.abspath(data_folder),
            os.path.abspath(log_folder),
            os.path.abspath(output_folder)
        ]

        if fake:
            args.insert(0, "--fake")

        self.env.run_bash_script('steps/compute_cmvn_stats.sh', args=args)