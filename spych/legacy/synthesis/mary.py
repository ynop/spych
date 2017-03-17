from spych.synthesis import synthesizer

from spych.tools import marytts


class MarySynthesizer(synthesizer.Synthesizer):
    """
    Implements a synthesizer using MaryTTS. MaryTTS server needs to be running.
    """

    def __init__(self, config=None, host=marytts.MARY_DEFAULT_HOST, port=marytts.MARY_DEFAULT_PORT):
        """
        Create Synthesizer. Needs a running maryTTS server.

        :param config: Config to use.
        :param host: Host where maryTTS is running.
        :param port: Port where maryTTS is listening.
        """
        synthesizer.Synthesizer.__init__(self, config=config)
        self.host = host
        self.port = port

        self.maryClient = marytts.MaryClient(host=host, port=port)

    def synthesize_text(self, text, path, voice=None, effects={}):
        self.maryClient.synthesize(text, path, voice=voice, locale=self._config.locale, effects=effects)
