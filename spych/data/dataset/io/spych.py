import collections
import glob
import os
import shutil

from spych import data
from spych.data import dataset
from spych.data.dataset.io import base
from spych.utils import jsonfile
from spych.utils import textfile

FILES_FILE_NAME = 'files.txt'
UTTERANCE_FILE_NAME = 'utterances.txt'
SPEAKER_INFO_FILE_NAME = 'speakers.json'
UTT2SPK_FILE_NAME = 'utt2spk.txt'
SEG_FILE_PREFIX = 'segmentation'
FEAT_CONTAINER_FILE_NAME = 'features.txt'


class SpychDatasetLoader(base.DatasetLoader):
    @classmethod
    def type(cls):
        return 'spych'

    def check_for_missing_files(self, path):
        necessary_files = [FILES_FILE_NAME, UTTERANCE_FILE_NAME]
        missing_files = []

        for file_name in necessary_files:
            file_path = os.path.join(path, file_name)

            if not os.path.isfile(file_path):
                missing_files.append(file_name)

        return missing_files or None

    def _load(self, loading_dataset):
        # Read files
        file_path = os.path.join(loading_dataset.path, FILES_FILE_NAME)
        for file_idx, file_path in textfile.read_key_value_lines(file_path, separator=' ').items():
            loading_dataset.add_file(os.path.abspath(os.path.join(loading_dataset.path, file_path)), file_idx=file_idx, copy_file=False)

        # Read speakers
        speaker_path = os.path.join(loading_dataset.path, SPEAKER_INFO_FILE_NAME)
        for speaker_idx, speaker_info in jsonfile.read_json_file(speaker_path).items():
            speaker = loading_dataset.add_speaker(speaker_idx=speaker_idx)
            speaker.load_speaker_info_from_dict(speaker_info)

        # Read utt2spk
        utt2spk_path = os.path.join(loading_dataset.path, UTT2SPK_FILE_NAME)
        if os.path.isfile(utt2spk_path):
            utt2spk = textfile.read_key_value_lines(utt2spk_path, separator=' ')

        # Read utterances
        utterance_path = os.path.join(loading_dataset.path, UTTERANCE_FILE_NAME)
        for utterance_idx, utt_info in textfile.read_separated_lines_with_first_key(utterance_path, separator=' ', max_columns=4).items():
            start = None
            end = None

            if len(utt_info) > 1:
                start = float(utt_info[1])

            if len(utt_info) > 2:
                end = float(utt_info[2])

            if utterance_idx in utt2spk.keys():
                speaker_idx = utt2spk[utterance_idx]
                loading_dataset.add_utterance(utt_info[0], utterance_idx=utterance_idx, speaker_idx=speaker_idx, start=start, end=end)

        # Read segmentations
        for seg_file in glob.glob(os.path.join(loading_dataset.path, 'segmentation_*.txt')):
            file_name = os.path.basename(seg_file)
            key = file_name[len('segmentation_'):len(file_name) - len('.txt')]

            utterance_segments = collections.defaultdict(list)

            for record in textfile.read_separated_lines_generator(seg_file, separator=' ', max_columns=4):
                utterance_segments[record[0]].append(data.Token(record[3], float(record[1]), float(record[2])))

            for utterance_idx, segments in utterance_segments.items():
                loading_dataset.add_segmentation(utterance_idx, segments=segments, key=key)

        # Read subviews
        for subview_file in glob.glob(os.path.join(loading_dataset.path, 'subview_*.txt')):
            file_name = os.path.basename(subview_file)
            sv_name = file_name[len('subview_'):len(file_name) - len('.txt')]

            sv = dataset.Subview()

            for key, value in textfile.read_separated_lines_with_first_key(subview_file, separator=' ').items():
                if key == 'filtered_utt_ids':
                    sv.filtered_utterance_idxs = set(value)
                elif key == 'filtered_speaker_ids':
                    sv.filtered_speaker_idxs = set(value)
                elif key == 'utterance_idx_patterns':
                    sv.utterance_idx_patterns = set(value)
                elif key == 'speaker_idx_patterns':
                    sv.speaker_idx_patterns = set(value)
                elif key == 'utterance_idx_not_patterns':
                    sv.utterance_idx_not_patterns = set(value)
                elif key == 'speaker_idx_not_patterns':
                    sv.speaker_idx_not_patterns = set(value)

            loading_dataset.add_subview(sv_name, sv)

        # Read features
        feat_path = os.path.join(loading_dataset.path, FEAT_CONTAINER_FILE_NAME)

        if os.path.isfile(feat_path):
            for container_name, container_path in textfile.read_key_value_lines(feat_path, separator=' ').items():
                loading_dataset.create_feature_container(container_name, container_path)

    def _save(self, saving_dataset, path, files, copy_files=False):
        # Write files
        file_path = os.path.join(path, FILES_FILE_NAME)
        file_records = files
        textfile.write_separated_lines(file_path, file_records, separator=' ', sort_by_column=0)

        # Write speakers
        speaker_path = os.path.join(path, SPEAKER_INFO_FILE_NAME)
        speaker_data = {speaker.idx: speaker.get_speaker_info_dict() for speaker in saving_dataset.speakers.values()}
        jsonfile.write_json_to_file(speaker_path, speaker_data)

        # Write utterances
        utterance_path = os.path.join(path, UTTERANCE_FILE_NAME)
        utterance_records = {utterance.idx: [utterance.file_idx, utterance.start, utterance.end] for utterance in saving_dataset.utterances.values()}
        textfile.write_separated_lines(utterance_path, utterance_records, separator=' ', sort_by_column=0)

        # Write utt2spk
        utt2spk_path = os.path.join(path, UTT2SPK_FILE_NAME)
        utt2spk_records = {utterance.idx: utterance.speaker_idx for utterance in saving_dataset.utterances.values()}
        textfile.write_separated_lines(utt2spk_path, utt2spk_records, separator=' ', sort_by_column=0)

        # Write segmentations
        segmentations_by_key = collections.defaultdict(dict)

        for utterance_idx, utt_segmentations in saving_dataset.segmentations.items():
            for key, segmentation in utt_segmentations.items():
                segmentations_by_key[key][utterance_idx] = segmentation

        for key, utt_segmentations in segmentations_by_key.items():
            file_path = os.path.join(path, '{}_{}.txt'.format(SEG_FILE_PREFIX, key))

            lines = []

            for utterance_idx in sorted(utt_segmentations.keys()):
                seg = utt_segmentations[utterance_idx]
                for segment in seg.segments:
                    lines.append('{} {} {} {}'.format(utterance_idx, segment.start, segment.end, segment.value))

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

        # Write subviews
        for name, sv in saving_dataset.subviews.items():
            subview_path = os.path.join(path, 'subview_{}.txt'.format(name))

            content = {
                'filtered_utt_ids': sv.filtered_utterance_idxs,
                'filtered_speaker_ids': sv.filtered_speaker_idxs,
                'utterance_idx_patterns': sv.utterance_idx_patterns,
                'speaker_idx_patterns': sv.speaker_idx_patterns,
                'utterance_idx_not_patterns': sv.utterance_idx_not_patterns,
                'speaker_idx_not_patterns': sv.speaker_idx_not_patterns
            }

            textfile.write_separated_lines(subview_path, content, separator=' ')

        # Write features
        feat_path = os.path.join(path, FEAT_CONTAINER_FILE_NAME)
        feat_records = {}

        for name, feature_container in saving_dataset.features.items():

            if copy_files and not os.path.samefile(saving_dataset.path, path):
                old_path = feature_container.path
                new_rel_path = 'features_{}'.format(name)
                target_abs_path = os.path.abspath(os.path.join(path, new_rel_path))

                feature_container.path = target_abs_path

                os.makedirs(target_abs_path, exist_ok=True)

                for utterance_idx in saving_dataset.utterances.keys():
                    src = os.path.join(old_path, '{}.npy'.format(utterance_idx))
                    target = os.path.join(target_abs_path, '{}.npy'.format(utterance_idx))
                    shutil.copy(src, target)

                feat_records[name] = new_rel_path
            else:
                feat_records[name] = os.path.relpath(feature_container.path, path)

        textfile.write_separated_lines(feat_path, feat_records, separator=' ')
