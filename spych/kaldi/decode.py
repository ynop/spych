import os

from spych.utils import textfile


class KaldiDecode(object):
    def __init__(self, env):
        self.env = env

    def make_graph(self, language_folder, model_folder, output_folder):
        """
        Creates training graph from model, lexicon and language model.
        :param language_folder: Path to the lang folder (with lexicon and language model).
        :param model_folder: Path to the model folder.
        :param output_folder: Path to the folder to put the graph into.
        :param monophone: Set True for monophone model.
        :param quinphone: Set True for quinphone model.
        :return:
        """
        args = [
            os.path.abspath(language_folder),
            os.path.abspath(model_folder),
            os.path.abspath(output_folder)
        ]

        self.env.run_bash_script('utils/mkgraph.sh', args=args)

    def decode(self, graph_folder, data_folder, decode_folder, model=None, number_of_jobs=4):
        """
        Decodes the given data with the given decoding graph.
        :param graph_folder: Path to folder with the graph.
        :param data_folder: Path to the data folder.
        :param decode_folder: Path to the folder to put decoding files into.
        :param number_of_jobs: Number of parallel jobs.
        :return:
        """
        args = [
            '--nj', str(number_of_jobs)
        ]

        if model is not None:
            args.append('--model')
            args.append(os.path.abspath(model))

        args.extend([
            os.path.abspath(graph_folder),
            os.path.abspath(data_folder),
            os.path.abspath(decode_folder)
        ])

        self.env.run_bash_script('steps/decode.sh', args=args)

    def create_dummy_reco2file(self, data_folder):
        data_folder = os.path.abspath(data_folder)

        wav_file = os.path.join(data_folder, 'wav.scp')

        wavs = textfile.read_key_value_lines(wav_file, separator=' ', )

        out = []

        for rec_id, rec_path in wavs.items():
            filename = os.path.splitext(os.path.basename(rec_path))[0]

            out.append([rec_id, filename, 'A'])

        reco_file = os.path.join(data_folder, 'reco2file_and_channel')
        textfile.write_separated_lines(reco_file, out, separator=' ')

    def get_ctm(self, data_folder, graph_folder, decode_folder):
        """
        Create word alignment in CTM format from decoding folder (lattice).
        :param data_folder: Path to data folder.
        :param graph_folder: Path to graph folder.
        :param decode_folder: Path to decode folder.
        :return:
        """
        self.env.run_bash_script('steps/get_ctm.sh', args=[
            os.path.abspath(data_folder),
            os.path.abspath(graph_folder),
            os.path.abspath(decode_folder)
        ])

    def latgen_faster_mapped(self, word_symbol_table, model, graph, in_path, out_path, min_active=200, max_active=7000, max_mem=50000000, beam=13.0,
                             lattice_beam=8.0, acoustic_scale=0.08, allow_partial=True, num_threads=1):
        cmd = [
            'latgen-faster-mapped-parallel' if num_threads > 1 else 'latgen-faster-mapped'
        ]

        if num_threads > 1:
            cmd.append('--num-threads={}'.format(num_threads))

        cmd.extend([
            '--min-active={}'.format(min_active),
            '--max-active={}'.format(max_active),
            '--max-mem={}'.format(max_mem),
            '--beam={}'.format(beam),
            '--lattice-beam={}'.format(lattice_beam),
            '--acoustic-scale={}'.format(acoustic_scale),
            '--allow-partial={}'.format('true' if allow_partial else 'false'),
            '--word-symbol-table={}'.format(word_symbol_table),
            os.path.abspath(model),
            os.path.abspath(graph),
            'ark:{}'.format(in_path),
            'ark:|gzip -c > {}'.format(out_path)
        ])

        self.env.run_cmd(cmd, stdin=None)

    def score(self, data, graph_dir, decode_dir, cmd='utils/run.pl', min_lmwt=4, max_lmwt=15):
        self.env.run_bash_script('local/score.sh', args=[
            '--min-lmwt', str(min_lmwt),
            '--max-lmwt', str(max_lmwt),
            '--cmd', cmd,
            os.path.abspath(data),
            os.path.abspath(graph_dir),
            os.path.abspath(decode_dir)
        ])
