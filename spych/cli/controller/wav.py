import os
import glob

from cement.core import controller

import scipy.io.wavfile

from spych.audio import signal
from spych.assets import audacity


class MainController(controller.CementBaseController):
    class Meta:
        label = 'wav'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Working with wav files."

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()


class AddNoiseController(controller.CementBaseController):
    class Meta:
        label = 'add-noise'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Add noise to wav files."

        arguments = [
            (['input-path'], dict(action='store', help='Path to the wav file to modify or a directory containing wav files.')),
            (['output-path'], dict(action='store', help='Path to store the modified wav or a directory to store modified wav files.')),
            (['--snr'], dict(action='store', help='Signal-to-Noise ratio to use for noise addition. (default 10 dB)', default='10')),
            (['--noise_path'], dict(action='store', help='Path to noise file. If not set random white-noise is added.'))
        ]

    @controller.expose(hide=True)
    def default(self):
        input_path = self.app.pargs.input_path
        output_path = self.app.pargs.output_path
        noise_path = self.app.pargs.noise_path
        snr = float(self.app.pargs.snr)

        if os.path.isdir(input_path):
            if not os.path.isdir(output_path) or os.path.samefile(input_path, output_path):
                print("If input is a directory output has to be another directory.")
            else:
                for wav_path in glob.glob(os.path.join(input_path, '*.wav')):
                    basename = os.path.basename(wav_path)
                    target_path = os.path.join(output_path, basename)

                    if noise_path is None:
                        signal.add_random_noise_to_wav(wav_path, target_path, snr=snr)
                    else:
                        signal.add_noise_to_wav(wav_path, noise_path, target_path, snr=snr)
        else:
            if os.path.isdir(output_path):
                basename = os.path.basename(input_path)
                target_path = os.path.join(output_path, basename)
            else:
                target_path = output_path

            if noise_path is None:
                signal.add_random_noise_to_wav(input_path, target_path, snr=snr)
            else:
                signal.add_noise_to_wav(input_path, noise_path, target_path, snr=snr)


class SegmentExtractionController(controller.CementBaseController):
    class Meta:
        label = 'extract-segments'
        stacked_on = 'wav'
        stacked_type = 'nested'
        description = "Extract segments from a wav."

        arguments = [
            (['wav-path'], dict(action='store', help='Path to wav file to extract segments from.')),
            (['output-path'], dict(action='store', help='Path to directory to store extracted segments as wav files.')),
            (['label-path'], dict(action='store', help='Audacity label file that defines the segments.'))
        ]

    @controller.expose(hide=True)
    def default(self):
        input_path = self.app.pargs.input_path
        output_path = self.app.pargs.output_path
        label_path = self.app.pargs.label_path

        if not os.path.isdir(output_path):
            print('output-path needs to be a directory.')
            return

        signal.clip_segments_from_wav(input_path, label_path, output_path)


class SNREstimationController(controller.CementBaseController):
    class Meta:
        label = 'calculate-snr'
        stacked_on = 'wav'
        stacked_type = 'nested'
        description = "Calculate Signal-to-Noise-Ratio between signal and noise wav."

        arguments = [
            (['signal_path'], dict(action='store', help='Path to wav file with signal.')),
            (['--label_path'], dict(action='store',
                                    help='Path to audacity label file. (Labels signal, speech are considered signal, other parts of file as noise.))')),
            (['--noise_path'], dict(action='store', help='Path to wav with noise.'))
        ]

    @controller.expose(hide=True)
    def default(self):
        signal_path = self.app.pargs.signal_path
        label_path = self.app.pargs.label_path
        noise_path = self.app.pargs.noise_path

        if label_path is not None:
            sampling_rate, samples = scipy.io.wavfile.read(signal_path)
            labels = audacity.read_label_file(label_path)
            snr = signal.estimate_snr_with_labels(samples, sampling_rate, labels)
            print("SNR : {}".format(snr))
        elif noise_path is not None:
            signal_sampling_rate, signal_samples = scipy.io.wavfile.read(signal_path)
            noise_sampling_rate, noise_samples = scipy.io.wavfile.read(noise_path)
            snr = signal.calculate_snr(signal_samples, noise_samples)
            print("SNR : {}".format(snr))
        else:
            print("You have to provide a label or a noise file.")
