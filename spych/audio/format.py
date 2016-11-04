import enum


class AudioFileType(enum.Enum):
    """
    Defines a audio file type.
    """
    wav = 1


class AudioFileFormat(object):
    """
    Defines an audio format.
    """

    def __init__(self, file_type=AudioFileType.wav, nr_of_channels=1, sampling_rate=16000, bits_per_sample=16):
        self.file_type = file_type
        self.nr_of_channels = nr_of_channels
        self.sampling_rate = sampling_rate
        self.bits_per_sample = bits_per_sample

    def matches_sound_header(self, sound_header):
        """
        Checks if the sound_header (sndhdr) matches this format.

        :param sound_header: SoundHeader obtained with sndhdr.what()
        :return: True if equal
        """
        return self.file_type.name == sound_header.filetype and \
               self.sampling_rate == sound_header.framerate and \
               self.nr_of_channels == sound_header.nchannels and \
               self.bits_per_sample == sound_header.sampwidth

    @classmethod
    def wav_mono_16bit_16k(cls):
        """
        Return format WAV, MONO, 16 bit, 16000

        :return: AudioFileFormat
        """
        return cls(file_type=AudioFileType.wav, nr_of_channels=1, sampling_rate=16000, bits_per_sample=16)
