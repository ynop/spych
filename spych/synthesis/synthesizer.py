import os


class Synthesizer(object):
    """
    Base class for any synthesizer implementation.
    """

    @classmethod
    def name(cls):
        return None

    def synthesize_text(self, text, path, voice=None, effects={}):
        """
        Synthesize the given text and save it at path.

        :param text: Text to synthesize.
        :param path: Path to store the audio file.
        :param voice: The name of the voice to use.
        :param effects: Dictionary with the effects to apply.
        """
        pass

    def synthesize_sentences(self, sentences, destination_folder, voice=None, effects={}):
        """
        Synthesize all sentences and save the files (ID as filename) in the given folder.

        sentences : {ID : SENTENCE}

        :param sentences: Dict with id/sentence pairs.
        :param destination_folder: Path to store the synthesized speech.
        :param voice: The name of the voice to use.
        :param effects: Dictionary with the effects to apply.
        """

        for sentence_id, sentence in sentences.items():
            file_name = sentence_id
            file_path = os.path.join(destination_folder, file_name)

            self.synthesize_text(sentence, file_path, voice, effects)
