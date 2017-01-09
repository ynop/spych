from cement.core import controller

from spych.audio import signal


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
