import collections
import copy
import os
import random
import shutil
import abc

import librosa

from spych import data
from spych.audio import signal
from spych.utils import naming


class DatasetBase(metaclass=abc.ABCMeta):
    """
    Defines the base interface for an audio dataset.
    """

    @property
    @abc.abstractmethod
    def name(self):
        """ Return the name of the dataset (Equals basename of the path, if not None). """
        return "undefined"

    @property
    @abc.abstractmethod
    def files(self):
        """ Return a dictionary containing file-objs with the file-id as key. """
        return {}

    @property
    @abc.abstractmethod
    def utterances(self):
        """ Return a dictionary containing utterance-objs with the utterance-id as key. """
        return {}

    @property
    @abc.abstractmethod
    def segmentations(self):
        """ Return a dictionary of dictionaries containing segmentation key/obj with the utterance-id as key. """
        return {}

    @property
    @abc.abstractmethod
    def speakers(self):
        """ Return a dictionary containing speaker-objs with the speaker-id as key. """
        return {}

    @property
    @abc.abstractmethod
    def features(self):
        """ Return a dictionary containing feature-containers with the feature-name as key. """
        return {}

    #
    #   Files
    #

    @property
    def num_files(self):
        """ Return number of files. """
        return len(self.files)

    def add_random_noise(self, snr=None, snr_range=None):
        """
        Adds generated noise to all files in the dataset with the given SNR.

        :param snr: Signal-to-Noise-Ratio [dB]
        :param snr_range: Uses a random Signal-to-Noise-Ratio [dB] in the given range (start,end)
        """
        for file in self.files.values():
            used_snr = snr

            if snr_range is not None:
                used_snr = random.randint(snr_range[0], snr_range[1])

            signal.add_random_noise_to_wav(file.path, file.path, snr=used_snr)

    #
    #   Utterances
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

    def read_utterance_data(self, utterance_idx, without_start_end_silence=False, word_alignment_key=None):
        """
        Read the audio signal for the given utterance. This uses librosa.core.load.

        :param utterance_idx: Utterance-Id to read signal for.
        :param without_start_end_silence: If True tries to cut off start and end silence based on word alignment.
        :param word_alignment_key: Key of the segmentation with the word alignment for silence cutoff.
        :return: tuple (nd-array samples, sampling-rate)
        """
        utt = self.utterances[utterance_idx]
        file_path = self.files[utt.file_idx].path

        start = utt.start
        end = utt.end

        if without_start_end_silence:
            if word_alignment_key is None:
                raise ValueError('You have to provide a key pointing to the word alignment segmentations to read without start/end silences.')

            seg = self.segmentations[utterance_idx][word_alignment_key]

            start += seg.first_segment.start
            end = utt.start + seg.last_segment.end

        if end != data.Utterance.END_FULL_FILE:
            samples, sampling_rate = librosa.core.load(file_path, sr=None, offset=start, duration=end - start)
        else:
            samples, sampling_rate = librosa.core.load(file_path, sr=None, offset=start)

        return samples, sampling_rate

    #
    #   Speakers
    #
    @property
    def num_speakers(self):
        """ Return the number of speakers in the dataset. """
        return len(self.speakers)

    #
    #   Segmentations
    #
    @property
    def all_segmentation_keys(self):
        """ Return a set of all occuring segmentation keys. """
        keys = set()

        for utt_idx, segmentations in self.segmentations.items():
            keys.update(segmentations.keys())

        return keys

    def all_segmentations_with_key(self, key):
        """ Return a set of all occurring segmentations with the given key. """
        raise NotImplementedError('Not yet implemented!')

    def num_segmentations_for_utterance(self, utterance_idx):
        """ Return the number of segmentations, the given utterance contains. """
        return len(self.segmentations[utterance_idx])

    #
    #   Features
    #
    def get_features(self, utterance_idx, feature_container):
        """ Return the features (np array) for the given utterance of the given container. """

        if feature_container in self.features.keys():
            return self.features[feature_container].load_features_of_utterance(utterance_idx)


class Dataset(DatasetBase):
    """
    Represents an audio dataset.

    Notes on paths:
    All paths stored in the dataset object (audio files, features) are absolute.

    :param path: Path to a directory on the filesystem, which acts as root folder for the dataset.
                If no path is given the dataset cannot be saved on disk.
    :param loader: This object is used to save the dataset. By default :class:`spych.data.dataset.io.SpychDatasetLoader` is used.
    :type loader: :class:`spych.data.dataset.io.DatasetLoader`
    """

    def __init__(self, path=None, loader=None):
        self.path = path

        if loader is None:
            from spych.data.dataset.io import spych
            self.loader = spych.SpychDatasetLoader()
        else:
            self.loader = loader

        self._files = {}
        self._utterances = {}
        self._segmentations = collections.defaultdict(dict)
        self._speakers = {}
        self.subviews = {}
        self._features = {}

    @property
    def files(self):
        return self._files

    @property
    def utterances(self):
        return self._utterances

    @property
    def segmentations(self):
        return self._segmentations

    @property
    def speakers(self):
        return self._speakers

    @property
    def features(self):
        return self._features

    @property
    def name(self):
        """
        Get the name of the dataset (Equals basename of the path, if not None.)
        :return: name
        """
        if self.path is None:
            return "undefined"
        else:
            return os.path.basename(os.path.abspath(self.path))

    def save(self):
        """ Save this dataset at self.path. """

        if self.path is None:
            raise ValueError('No path given to save the dataset.')

        self.save_at(self.path)

    def save_at(self, path, loader=None, copy_files=False):
        """
        Save this dataset at the given path. If the path differs from the current path set, the path gets updated.

        :param path: Path to save the dataset to.
        :param loader: If you want to use another loader (e.g. to export to another format). Otherwise it uses the loader associated with this dataset.
        :param copy_files: If true the files are also stored in the new path, if not already there.
        """
        if loader is None:
            self.loader.save(self, path, copy_files=copy_files)
        elif type(loader) == str:
            from ..dataset import io
            loader = io.create_loader_of_type(loader)
            loader.save(self, path, copy_files=copy_files)
        else:
            loader.save(self, path, copy_files=copy_files)

        self.path = path

    @classmethod
    def load(cls, path, loader=None):
        """ Loads the dataset from the given path, using the given loader. If no loader is given the spych loader is used. """

        if loader is None:
            from ..dataset import io
            loader = io.SpychDatasetLoader()
        elif type(loader) == str:
            from ..dataset import io
            loader = io.create_loader_of_type(loader)

        return loader.load(path)

    #
    #   Subview
    #

    @property
    def num_subviews(self):
        """ Return number of subviews. """
        return len(self.subviews)

    def add_subview(self, name, subview):
        """ Add the subview to this dataset. """
        subview.dataset = self
        self.subviews[name] = subview

    def export_subview(self, name):
        """ Return a subview as a standalone dataset. """
        sv = self.subviews[name]

        exported_set = Dataset(path=self.path)
        exported_set._files = copy.deepcopy(sv.files)
        exported_set._utterances = copy.deepcopy(sv.utterances)
        exported_set._speakers = copy.deepcopy(sv.speakers)
        exported_set._segmentations = copy.deepcopy(sv.segmentations)
        exported_set._features = copy.deepcopy(sv.features)

        return exported_set

    #
    # File
    #
    def add_file(self, path, file_idx=None, copy_file=False):
        """
        Adds a new file to the dataset.

        :param path: Path of the file to add.
        :param file_idx: The id to associate the file with. If None or already exists, one is generated.
        :param copy_file: If True the file is copied to the dataset folder, otherwise the given path is used directly.
        :return: File object
        """

        if copy_file and not os.path.isdir(self.path):
            raise ValueError('No path defined for this dataset, cannot copy files.')

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
                full_path = os.path.abspath(os.path.join(self.path, final_file_path))

            shutil.copy(path, full_path)
        else:
            if os.path.isabs(path):
                final_file_path = path
            else:
                final_file_path = os.path.abspath(path)

        file_obj = data.File(final_file_idx, final_file_path)
        self.files[final_file_idx] = file_obj

        return file_obj

    def remove_files(self, file_ids, delete_files=False):
        """
        Deletes the given wavs.

        :param file_ids: List of file_idx's or fileobj's
        :param delete_files: Also delete the files
        """

        for file_idx in file_ids:
            if type(file_idx) == data.File:
                file_obj = file_idx
            else:
                file_obj = self.files[file_idx]

            if delete_files:
                path = os.path.join(self.path, file_obj.path)
                if os.path.exists(path):
                    os.remove(path)

            self.remove_utterances(self.utterances_in_file(file_idx))

            del self.files[file_obj.idx]

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

        utt = data.Utterance(final_utterance_idx, file_idx, speaker_idx=speaker_idx, start=start, end=end)
        self.utterances[final_utterance_idx] = utt

        return utt

    def remove_utterances(self, utterance_ids):
        """
        Removes the given utterances by id.

        :param utterance_ids: List of utterance ids
        """
        for utt_id in utterance_ids:
            if type(utt_id) == data.Utterance:
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

        spk = data.Speaker(final_speaker_idx, gender=gender)
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
            segmentation_obj = data.Segmentation.from_text(segments, utterance_idx=utterance_idx, key=key)
        elif type(segments) == list:
            segmentation_obj = data.Segmentation(segments=segments, utterance_idx=utterance_idx, key=key)
        else:
            return None

        self.segmentations[utterance_idx][segmentation_obj.key] = segmentation_obj

        return segmentation_obj

    def import_segmentation(self, segmentation):
        """ Adds an existing segmentation to the dataset. Uses key and utterance-id from the segmentation object. """

        if segmentation.utterance_idx is None or segmentation.utterance_idx.strip() == '':
            raise ValueError('No utterance id given. The segmentation has to be associated with an utterance!')

        if segmentation.utterance_idx not in self.utterances.keys():
            raise ValueError('Utterance with id {} does not exist!'.format(segmentation.utterance_idx))

        self.segmentations[segmentation.utterance_idx][segmentation.key] = segmentation

        return segmentation

    #
    #   FEATURES
    #

    def add_new_feature_container(self, name, path):
        """ Create a new feature container """

        if name in self.features.keys():
            raise ValueError('Feature container with name {} already exists.'.format(name))

        if os.path.isabs(path):
            final_feature_path = path
        else:
            final_feature_path = os.path.join(self.path, path)

        os.makedirs(final_feature_path, exist_ok=True)
        self.features[name] = data.FeatureContainer(final_feature_path, dataset=self)

    def add_features(self, utterance_idx, feature_matrix, feature_container):
        """
        Adds the given features to the dataset. Features are stored directly to the filesystem, so this dataset has to have a path set.

        :param utterance_idx: Utterance to which the features correspond.
        :param feature_matrix: A numpy array containing the features.
        :param feature_container: Name of the container to store the features in.
        """

        if feature_container not in self.features.keys():
            raise ValueError('No feature container with name {} exists.'.format(feature_container))

        if utterance_idx is None or utterance_idx.strip() == '':
            raise ValueError('No utterance id given. The features have to be associated with an utterance!')

        if utterance_idx not in self.utterances.keys():
            raise ValueError('Utterance with id {} does not exist!'.format(utterance_idx))

        self.features[feature_container].add_features_for_utterance(utterance_idx, feature_matrix)

    #
    #   DIV
    #

    def import_dataset(self, import_dataset, copy_files=False):
        """
        Merges the given dataset into this dataset.

        :param import_dataset: Dataset to merge
        :param copy_files: If True moves the wavs to this datasets folder.
        """

        if copy_files and not os.path.isdir(self.path):
            raise ValueError('No path defined for this dataset, cannot copy files.')

        file_idx_mapping = {}

        for file_idx, file_to_import in import_dataset.files.items():
            imported_file = self.add_file(os.path.abspath(os.path.join(import_dataset.path, file_to_import.path)), file_idx=file_idx,
                                          copy_file=copy_files)
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
                                                    end=utterance_to_import.end)
            utt_idx_mapping[utt_id] = imported_utterance.idx

        for utt_id, keys in import_dataset.segmentations.items():
            for key, seg in keys.items():
                import_utt_id = utt_idx_mapping[utt_id]
                self.add_segmentation(import_utt_id, segments=seg.segments, key=key)

    #
    #   MODIFICATIONS
    #

    def subdivide_speakers(self, target_number_of_speakers):
        """
        Divide the available speakers in the dataset into different speakers so the number of speakers is target_number_of_speakers.

        :param target_number_of_speakers: Target number of speakers
        """

        if self.num_speakers >= target_number_of_speakers:
            print("Number of speakers already greater or equal to {}.".format(target_number_of_speakers))
            return

        spk2utt = self.speaker_to_utterance_dict()
        spk2utt_count = {speaker_id: len(utterances) for speaker_id, utterances in spk2utt.items()}

        utt_count = sum(spk2utt_count.values())

        target_num_utts_per_speaker = int(utt_count / target_number_of_speakers)

        # at least one part per speaker
        spk2num_parts = {speaker_id: 1 for speaker_id, utt_count in spk2utt_count.items()}
        spk2utt_count_intermediate = {speaker_id: utt_count - target_num_utts_per_speaker for speaker_id, utt_count in spk2utt_count.items()}

        num_assigned_parts = len(spk2num_parts)

        for i in range(num_assigned_parts, target_number_of_speakers):
            sorted_spk2utt_count = sorted(spk2utt_count_intermediate.items(), key=lambda t: t[1], reverse=True)
            spk2utt_count_intermediate[sorted_spk2utt_count[0][0]] -= target_num_utts_per_speaker
            spk2num_parts[sorted_spk2utt_count[0][0]] += 1

        for speaker_id, num_parts in spk2num_parts.items():
            num_utts = spk2utt_count[speaker_id]
            num_utts_per_part = int(num_utts / num_parts)
            num_utts_rest = num_utts % num_parts

            start_index = 0
            shuffled_utt_ids = list(spk2utt[speaker_id])
            random.shuffle(shuffled_utt_ids)

            for i in range(num_parts):
                num_utts_new = num_utts_per_part

                if num_utts_rest > 0:
                    num_utts_new += 1
                    num_utts_rest -= 1

                if i > 0:
                    new_speaker_id = naming.generate_name(15, not_in=self.speakers.keys())
                    new_speaker = self.add_speaker(new_speaker_id)
                    new_speaker.load_speaker_info_from_dict(self.speakers[speaker_id].get_speaker_info_dict())
                    new_speaker.part_from_speaker = speaker_id

                    part_utt_ids = shuffled_utt_ids[start_index:start_index + num_utts_new]

                    for utt_id in part_utt_ids:
                        if utt_id.starts_with(speaker_id):
                            changed_utt_id = utt_id.replace(speaker_id, new_speaker_id)
                        else:
                            changed_utt_id = naming.generate_name(15, not_in=self.utterances.keys())

                        self.utterances[changed_utt_id] = self.utterances[utt_id]
                        self.utterances[changed_utt_id].idx = changed_utt_id

                        del self.utterances[utt_id]

                        self.segmentations[changed_utt_id] = self.segmentations[utt_id]

                        for key, seg in self.segmentations[changed_utt_id].items():
                            seg.utterance_idx = changed_utt_id

                        del self.segmentations[utt_id]

                start_index += num_utts_new
