import os
import re


class KaldiTrain(object):
    def __init__(self, env):
        self.env = env

    def train_mono(self, data_folder, language_folder, output_folder, cmd='utils/run.pl', number_of_jobs=4):
        """
        Monophone training.
        :param data_folder: Path to folder with the data.
        :param language_folder: Path to language folder.
        :param output_folder: Path to the folder to put model files into.
        :param number_of_jobs: Number of parallel jobs.
        :return:
        """
        self.env.run_bash_script('steps/train_mono.sh', args=[
            '--nj', str(number_of_jobs),
            '--cmd', cmd,
            os.path.abspath(data_folder),
            os.path.abspath(language_folder),
            os.path.abspath(output_folder)
        ])

    def train_deltas(self, data_folder, language_folder, base_model_folder, output_folder, cmd='utils/run.pl', number_of_leaves=2500,
                     tot_gauss=30000):
        """
        Delta training.
        :param data_folder: Path to folder with the data.
        :param language_folder: Path to language folder.
        :param base_model_folder: Path to the folder with the base model to train deltas on.
        :param output_folder: Path to the folder to put model files into.
        :param number_of_leaves: ...
        :param tot_gauss: ...
        :return:
        """
        self.env.run_bash_script('steps/train_deltas.sh', args=[
            '--cmd', cmd,
            str(number_of_leaves),
            str(tot_gauss),
            os.path.abspath(data_folder),
            os.path.abspath(language_folder),
            os.path.abspath(base_model_folder),
            os.path.abspath(output_folder)
        ])

    def align(self, data_folder, language_folder, model_folder, output_folder, cmd='utils/run.pl', number_of_jobs=4):
        """
        Computes training alignments.
        :param data_folder: Path to folder with the data.
        :param language_folder: Path to language folder.
        :param model_folder: Path to the model folder.
        :param output_folder: Path to folder to put alignments.
        :param number_of_jobs: Number of parallel jobs.
        :return:
        """
        self.env.run_bash_script('steps/align_si.sh', args=[
            '--nj', str(number_of_jobs),
            '--cmd', cmd,
            os.path.abspath(data_folder),
            os.path.abspath(language_folder),
            os.path.abspath(model_folder),
            os.path.abspath(output_folder)
        ])

    def train_nnet(self, train_data_folder, dev_data_folder, lang_folder, train_ali_folder, dev_ali_folder, output_folder, hid_dim=2048, hid_layers=5,
                   lr=0.008, cmd='utils/run.pl'):
        self.env.run_bash_script(cmd, args=[
            'steps/train_nnet.sh',
            '--hid-dim', hid_dim,
            '--hid-layers', hid_layers,
            '--learn-rate', lr,
            train_data_folder,
            dev_data_folder,
            lang_folder,
            train_ali_folder,
            dev_ali_folder,
            output_folder
        ])

    def extract_posteriors(self, model_folder):
        model_file = os.path.join(model_folder, 'final.mdl')

        with open(os.path.join(model_folder, 'num_jobs'), 'r') as f:
            num_jobs = int(f.read().strip())

        for jobId in range(1, num_jobs + 1):
            ali_file = os.path.join(model_folder, "ali.{}.gz".format(jobId))

            post_ark = os.path.join(model_folder, "posts.{}.ark".format(jobId))
            post_scp = os.path.join(model_folder, "posts.{}.scp".format(jobId))

            pdfs = self.env.run_cmd([
                'ali-to-pdf',
                model_file,
                'ark:gunzip -c {} |'.format(ali_file),
                'ark:-'
            ], stdin=None)

            posts = self.env.run_cmd([
                'ali-to-post',
                'ark:-',
                'ark,scp:{},{}'.format(post_ark, post_scp)
            ], stdin=pdfs)

        concat_posts_scp = os.path.join(model_folder, 'posts.scp')
        with open(concat_posts_scp, 'w') as f:
            for jobId in range(1, num_jobs + 1):
                post_scp = os.path.join(model_folder, "posts.{}.scp".format(jobId))
                with open(post_scp, 'r') as sub_file:
                    f.writelines(sub_file.readlines())

    def get_num_pdf(self, model_path):
        # hmm-info final.mdl
        # number of phones 949
        # number of pdfs 1666
        # number of transition-ids 45256
        # number of transition-states 22608

        model_file = os.path.join(model_path, 'final.mdl')

        out = self.env.run_cmd(['hmm-info', model_file], stdin=None).decode('utf-8')

        pattern = re.compile(r'number of pdfs (\d*)')
        m = pattern.search(out)

        if m is not None:
            return int(m.group(1))
