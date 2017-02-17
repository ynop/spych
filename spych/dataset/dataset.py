import os
import collections
import shutil

from spych.dataset import file
from spych.dataset import utterance
from spych.dataset import speaker
from spych.dataset import segmentation

from spych.utils import naming


class Dataset(object):
    def __init__(self, path):
        self.path = path
        self.files = {}
        self.utterances = {}
        self.segmentations = collections.defaultdict(dict)
        self.speakers = {}

    @property
    def name(self):
        """
        Get the name of the dataset (= basename)
        :return: name
        """
        return os.path.basename(self.path)

    #
    #   File
    #

    def add_file(self, path, file_idx=None, copy_file=False):
        """
        Adds a new file to the dataset.

        :param path: Path of the file to add.
        :param file_idx: The id to associate the file with. If None or already exists, one is generated.
        :param copy_file: If True the file is copied to the dataset folder, otherwise the given path is used directly.
        :return: File object
        """

        if file_idx is None or file_idx in self.files.keys():
            final_file_idx = naming.generate_name(length=15, not_in=self.files.keys())
        else:
            final_file_idx = file_idx

        if copy_file:
            basename = os.path.basename(path)
            final_file_path = basename
            full_path = os.path.join(self.path, final_file_path)

            while os.path.exists(full_path):
                final_file_path =  '{}.wav'.format(naming.generate_name(15))
                full_path = os.path.join(self.path, final_file_path)

            shutil.copy(path, full_path)
        else:
            final_file_path = os.path.relpath(path, self.path)

        file_obj = file.File(final_file_idx, final_file_path)
        self.files[final_file_idx] = file_obj

        return file_obj

    #
    #   Utterance
    #

    def add_utterance(self, file_idx, utterance_idx=None, speaker_idx=None, start=0, end=-1):
        """
        Adds a new utterance to the dataset.

        :param file_idx: The file id the utterance is in.
        :param utterance_idx: The id to associate with the utterance. If None or already exists, one is generated.
        :param speaker_idx: The speaker id to associate with the utterance.
        :param start: Start of the utterance within the file [seconds].
        :param end: End of the utterance within the file [seconds]. -1 equals the end of the file.
        :return: Utterance object
        """

        if file_idx is None or file_idx.strip() == '':
            raise ValueError('No file id given. The utterance has to be associated with a file!')

        if file_idx not in self.files.keys():
            raise ValueError('File with id {} does not exist!'.format(file_idx))

        if speaker_idx is not None and speaker_idx not in self.speakers.keys():
            raise ValueError('Speaker with id {} does not exist!'.format(speaker_idx))

        if utterance_idx is None or utterance_idx in self.utterances.keys():
            final_utterance_idx = naming.generate_name(length=15, not_in=self.utterances.keys())
        else:
            final_utterance_idx = utterance_idx

        utt = utterance.Utterance(final_utterance_idx, file_idx, speaker_idx=speaker_idx, start=start, end=end)
        self.utterances[final_utterance_idx] = utt

        return utt

    #
    #   Speaker
    #

    def add_speaker(self, speaker_idx=None, gender=None):
        """
        Adds a new speaker to the dataset.

        :param speaker_idx: The id to associate the speaker with. If None or already exists, one is generated.
        :param gender: Gender of the speaker.
        :return: Speaker object
        """

        if speaker_idx is None or speaker_idx in self.speakers.keys():
            final_speaker_idx = naming.generate_name(length=15, not_in=self.speakers.keys())
        else:
            final_speaker_idx = speaker_idx

        spk = speaker.Speaker(final_speaker_idx, gender=gender)
        self.speakers[final_speaker_idx] = spk

        return spk

    #
    #   Segmentation
    #

    def add_segmentation(self, utterance_idx, segments=None, key=None):
        """
        Adds a new segmentation.

        :param utterance_idx: Utterance id the segmentation is associated with.
        :param segments: Segments can be a string (will be space separated into tokens) or a list of segments.
        :param key: A key this segmentation is assiciated with. (If None the default key is used.)
        :return: Segmentation object
        """

        if utterance_idx is None or utterance_idx.strip() == '':
            raise ValueError('No utterance id given. The segmentation has to be associated with an utterance!')

        if utterance_idx not in self.utterances.keys():
            raise ValueError('Utterance with id {} does not exist!'.format(utterance_idx))

        if type(segments) == str:
            segmentation_obj = segmentation.Segmentation.from_text(segments, utterance_idx=utterance_idx, key=key)
        elif type(segments) == list:
            segmentation_obj = segmentation.Segmentation(segments=segments, utterance_idx=utterance_idx, key=key)

        self.segmentations[utterance_idx][segmentation_obj.key] = segmentation_obj

        return segmentation_obj
