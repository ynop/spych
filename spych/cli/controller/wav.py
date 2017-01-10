from cement.core import controller

import scipy.io.wavfile

from spych.audio import signal
from spych.assets import audacity


class WavController(controller.CementBaseController):
    class Meta:
        label = 'wav'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Modifying wavs."

        arguments = [
            (['input_path'], dict(action='store', help='Path to the wav file to modify.')),
            (['output_path'], dict(action='store', help='Path to store the modified wav.')),
            (['--snr'], dict(action='store', help='Signal-to-Noise ratio to use for noise addition.'))
        ]

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

    @controller.expose(help="Print information about a given lexicon.", aliases_only=["add-random-noise"])
    def add_random_noise(self):
        input_path = self.app.pargs.input_path
        output_path = self.app.pargs.output_path
        snr = None

        if self.app.pargs.snr:
            snr = float(self.app.pargs.snr)

        signal.add_random_noise_to_wav(input_path, output_path, snr=snr)


class SNRController(controller.CementBaseController):
    class Meta:
        label = 'snr'
        stacked_on = 'wav'
        stacked_type = 'nested'
        description = "Calculate Signal-to-Noise-Ratio"

        arguments = [
            (['signal_path'], dict(action='store', help='Path to wav with signal.')),
            (['--label_path'], dict(action='store', help='Path to audacity label file.')),
            (['--noise_path'], dict(action='store', help='Path to wav with noise.'))
        ]

    @controller.expose(hide=True)
    def default(self):
        signal_path = self.app.pargs.signal_path
        label_path = None
        noise_path = None

        if self.app.pargs.label_path:
            label_path = self.app.pargs.label_path

        if self.app.pargs.noise_path:
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
