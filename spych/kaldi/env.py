import os
import itertools
import subprocess
import shlex
import logging


class KaldiEnv(object):

    def __init__(self, kaldi_root_path):
        self.root_path = kaldi_root_path
        self.script_path = os.path.join(self.root_path, 'egs', 'wsj', 's5')

        self._setup_env()

    def run_bash_script(self, command, args=[]):
        """ Executes the given command in the wsj folder. """
        cwd = os.getcwd()

        command = '/bin/bash {} {}'.format(command, ' '.join(args))
        args = shlex.split(command)

        logging.info("EXECUTE {}".format(command))

        os.chdir(self.script_path)
        os.system(command)
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        while process.poll() is None:
            self.log_outputs(process)

        self.log_outputs(process)

        process.wait()

        os.chdir(cwd)

    def run_cmd(self, cmd, stdin):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        stdout = p.communicate(input=stdin)[0]

        return stdout

    def _setup_env(self):
        srilm_root = os.path.join(self.root_path, 'tools', 'srilm')

        kaldi_root_subpaths = [
            'src/bin',
            'tools/openfst/bin',
            'src/fstbin',
            'src/gmmbin',
            'src/featbin',
            'src/lm',
            'src/sgmmbin',
            'src/sgmm2bin',
            'src/fgmmbin',
            'src/latbin',
            'src/nnetbin',
            'src/nnet2bin',
            'src/kwsbin',
            'src/online2bin',
            'src/ivectorbin',
            'src/lmbin',
            'src/nnet3bin'
        ]

        srilm_root_subpaths = [
            'bin',
            'bin/macosx'
        ]

        kaldi_paths = [os.path.join(self.root_path, subpath) for subpath in kaldi_root_subpaths]
        srilm_paths = [os.path.join(srilm_root, subpath) for subpath in srilm_root_subpaths]

        paths = ':'.join(itertools.chain([os.environ['PATH']], kaldi_paths, srilm_paths))

        os.environ['PATH'] = paths
        os.environ['SRILM_ROOT'] = srilm_root
        os.environ['LC_ALL'] = 'C'

    def log_outputs(self, process):
        l = process.stdout.readline()
        if l:
            l = l.strip('\n')
            logging.info(l)

        e = process.stderr.readline()
        if e:
            e = e.strip('\n')
            logging.error(e)