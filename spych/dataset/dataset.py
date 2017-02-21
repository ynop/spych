import os
import collections
import shutil

from spych.dataset import file
from spych.dataset import utterance
from spych.dataset import speaker
from spych.dataset import segmentation

from spych.utils import naming


class Dataset(object):
    """
    Represents a audio dataset.

    files: file-id -> file-obj
    utterances: utterance-id -> utterance-obj
    segmentations: utterance-id -> key -> segmentation-obj
    speakers: speaker-id -> speaker-obj
    subsets: subset-id -> list of utterance-id

    """

    def __init__(self, path, loader=None):
        self.path = path
        self.loader = loader
        self.files = {}
        self.utterances = {}
        self.segmentations = collections.defaultdict(dict)
        self.speakers = {}
        self.subsets = collections.defaultdict(list)

    @property
    def name(self):
        """
        Get the name of the dataset (= basename)
        :return: name
        """
        return os.path.basename(self.path)

    #
    #   Subset
    #

    def add_subset(self, name, utterances=[]):
        """ Create a subset with the given utterance-idx's. """
        if name in self.subsets.keys():
            raise ValueError('Subset with name {} already existing.'.format(name))

        self.subsets[name] = list(utterances)

    #
    # File
    #

    @property
    def num_files(self):
        """ Return number of files. """
        return len(self.files)

    def set_relative_wav_paths(self, path):
        """ Sets the given relative path for all wav files. Removes old path if exists. Basename stays as before. """
        for file_obj in self.files.values():
            file_obj.set_relative_path(path)

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
                final_file_path = '{}.wav'.format(naming.generate_name(15))
                full_path = os.path.join(self.path, final_file_path)

            shutil.copy(path, full_path)
        else:
            final_file_path = os.path.relpath(path, self.path)

        file_obj = file.File(final_file_idx, final_file_path)
        self.files[final_file_idx] = file_obj

        return file_obj

    def remove_files(self, file_ids, remove_files=False):
        """
        Deletes the given wavs.

        :param file_ids: List of file_idx's or fileobj's
        :param remove_files: Also delete the files
        """

        for file_idx in file_ids:
            if type(file_idx) == file.File:
                file_obj = file_idx
            else:
                file_obj = self.files[file_idx]

            if remove_files:
                path = os.path.join(self.path, file_obj.path)
                if os.path.exists(path):
                    os.remove(path)

            self.remove_utterances(self.utterances_in_file(file_idx))

            del self.files[file_obj.idx]

    #
    #   Utterance
    #

    @property
    def num_utterances(self):
        """ Return number of utterances. """
        return len(self.utterances)

    def utterances_in_file(self, file_idx):
        """ Return all utterances that are in the given file. """

        utterances = set()

        for utt in self.utterances.values():
            if utt.file_idx == file_idx:
                utterances.add(utt)

        return utterances

    def utterances_of_speaker(self, speaker_idx):
        """ Returns all utterances of the given speaker. """
        utterances = set()

        for utt in self.utterances.values():
            if utt.speaker_idx == speaker_idx:
                utterances.add(utt)

        return utterances

    def speaker_to_utterance_dict(self):
        """ Return a dict with speaker to utterances mapping. """

        spk2utt = collections.defaultdict(list)

        for utt in self.utterances.values():
            spk = self.speakers[utt.speaker_idx]
            spk2utt[spk].append(utt)

        return spk2utt

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

    def remove_utterances(self, utterance_ids):
        """
        Removes the given utterances by id.

        :param utterance_ids: List of utterance ids
        """
        for utt_id in utterance_ids:
            if type(utt_id) == utterance.Utterance:
                utt = utt_id
            else:
                utt = self.utterances[utt_id]

            if utt.idx in self.utterances.keys():
                del self.utterances[utt.idx]

            if utt.idx in self.segmentations.keys():
                del self.segmentations[utt.idx]

    #
    #   Speaker
    #

    @property
    def num_speakers(self):
        """ Return the number of speakers in the dataset. """
        return len(self.speakers)

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

    def all_segmentations_with_key(self, key):
        """ Return a set of all occurring segmentations with the given key. """
        raise NotImplementedError('Not yet implemented!')

    def num_segmentations_for_utterance(self, utterance_idx):
        """ Return the number of segmentations, the given utterance contains. """
        return len(self.segmentations[utterance_idx])

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
        else:
            return None

        self.segmentations[utterance_idx][segmentation_obj.key] = segmentation_obj

        return segmentation_obj

    #
    #   DIV
    #

    def import_dataset(self, import_dataset, copy_files=False):
        """
        Merges the given dataset into this dataset.

        :param dataset: Dataset to merge
        :param copy_files: If True moves the wavs to this datasets folder.
        """

        file_idx_mapping = {}

        for file_idx, file_to_import in import_dataset.files.items():
            imported_file = self.add_file(file_to_import.path, file_idx=file_idx, copy_file=copy_files)
            file_idx_mapping[file_idx] = imported_file.idx

        speaker_idx_mapping = {}

        for speaker_idx, speaker_to_import in import_dataset.speakers.items():
            imported_speaker = self.add_speaker(speaker_idx=speaker_idx, gender=speaker_to_import.gender)
            speaker_idx_mapping[speaker_idx] = imported_speaker.idx

        utt_idx_mapping = {}

        for utt_id, utterance_to_import in import_dataset.utterances.items():
            import_file_idx = file_idx_mapping[utterance_to_import.file_idx]
            import_speaker_idx = speaker_idx_mapping[utterance_to_import.speaker_idx]
            imported_utterance = self.add_utterance(file_idx=import_file_idx,
                                                    utterance_idx=utt_id,
                                                    speaker_idx=import_speaker_idx,
                                                    start=utterance_to_import.start,
                                                    end=utterance_to_import.file_idx)
            utt_idx_mapping[utt_id] = imported_utterance.idx

        for utt_id, keys in import_dataset.segmentations.items():
            for key, seg in keys.items():
                import_utt_id = utt_idx_mapping[utt_id]
                self.add_segmentation(import_utt_id, segments=seg.segments, key=key)

        #
        #   SUBSETS
        #

        def create_subset_with_utterances(utterances, target_path):
            """ Create a subset with the given utterance-idx's at the given path. """
            pass

        def create_subset_with_speakers(speakers, target_path):
            """ Create a subset with the given speaker-idx's at the given path. """
            pass