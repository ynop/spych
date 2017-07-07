import struct

import numpy as np

from . import env
from . import features
from . import data
from . import train
from . import decode


class Kaldi(object):
    def __init__(self, kaldi_root):
        self.env = env.KaldiEnv(kaldi_root)
        self.data = data.KaldiData(self.env)
        self.features = features.KaldiFeatures(self.env)
        self.train = train.KaldiTrain(self.env)
        self.decode = decode.KaldiDecode(self.env)


def read_posteriors(rx_specifier, num_posts):
    """ Return float matrix as np array for the given rx specifier. """

    path, offset = rx_specifier.strip().split(':', maxsplit=1)
    offset = int(offset)
    sample_format = 4

    with open(path, 'rb') as f:
        # move to offset
        f.seek(offset)

        # assert binary ark
        binary = f.read(2)
        assert (binary == b'\x00B')

        format = f.read(1)
        assert (format == b'\x04')

        # get number frames
        num_frames = struct.unpack('<i', f.read(4))[0]

        matrix = np.zeros((num_frames, num_posts)).astype(np.float32)

        for frame_index in range(num_frames):
            assert (f.read(1) == b'\x04')

            num_values = struct.unpack('<i', f.read(4))[0]

            for value_index in range(num_values):
                assert (f.read(1) == b'\x04')
                pdf_id = struct.unpack('<i', f.read(4))[0]

                assert (f.read(1) == b'\x04')
                post = struct.unpack('<f', f.read(4))[0]

                matrix[frame_index][pdf_id] = post

        return matrix


def write_posteriors(ark_path, ds, feat_name):
    fc = ds.features[feat_name]
    fc.open()

    f = open(ark_path, 'wb')

    for utt_id in ds.utterances.keys():
        feats = fc.get(utt_id)

        f.write(('{} '.format(utt_id)).encode('utf-8'))

        f.write(b'\x00B')
        f.write(b'\x04')

        f.write(struct.pack('<i', np.size(feats, 0)))

        for frame in feats:
            f.write(b'\x04')

            active_states = np.where(frame > 0.0)[0]

            f.write(struct.pack('<i', np.size(active_states, 0)))

            for state_index in active_states:
                f.write(b'\x04')
                f.write(struct.pack('<i', state_index))
                f.write(b'\x04')
                f.write(struct.pack('<f', frame[state_index]))

    f.close()
    fc.close()


def write_likelihoods(ark_path, ds, feat_name, priors=None, floor_threshold=1e-4, floor_value=1e-20):
    fc = ds.features[feat_name]
    fc.open()

    f = open(ark_path, 'wb')

    for utt_id in ds.utterances.keys():
        feats = fc.get(utt_id)

        assert feats.dtype == np.float32, "Wrong feat number format (Expected float32)"
        assert not np.isnan(feats).any(), "NaN in feature matrix, {}".format(utt_id)
        assert not np.isinf(feats).any(), "INF in feature matrix, {}".format(utt_id)

        if priors is not None:
            feats += floor_value
            feats = np.where(feats < floor_threshold, floor_value, feats)
            feats = np.log(feats)
            feats -= priors

        f.write(('{} '.format(utt_id)).encode('utf-8'))

        f.write(b'\x00B')
        f.write(b'FM ')
        f.write(b'\x04')
        f.write(struct.pack('<i', np.size(feats, 0)))
        f.write(b'\x04')
        f.write(struct.pack('<i', np.size(feats, 1)))

        flattened = feats.reshape(np.size(feats, 0) * np.size(feats, 1))
        flattened.tofile(f, sep="")

    f.close()
    fc.close()
