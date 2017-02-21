import os
import collections
import glob

from spych.dataset.io import base
from spych.dataset import segmentation

from spych.utils import textfile
from spych.utils import jsonfile

FILES_FILE_NAME = 'files.txt'
UTTERANCE_FILE_NAME = 'utterances.txt'
SPEAKER_INFO_FILE_NAME = 'speakers.json'
UTT2SPK_FILE_NAME = 'utt2spk.txt'
SEG_FILE_PREFIX = 'segmentation'


class SpychDatasetLoader(base.DatasetLoader):
    @classmethod
    def type(self):
        return 'spych'

    def check_for_missing_files(self, path):
        necessary_files = [FILES_FILE_NAME, UTTERANCE_FILE_NAME]
        missing_files = []

        for file_name in necessary_files:
            file_path = os.path.join(path, file_name)

            if not os.path.isfile(file_path):
                missing_files.append(file_name)

        return missing_files or None

    def _load(self, dataset):
        # Read files
        file_path = os.path.join(dataset.path, FILES_FILE_NAME)
        for file_idx, file_path in textfile.read_key_value_lines(file_path, separator=' ').items():
            dataset.add_file(file_path, file_idx=file_idx, copy_file=False)

        # Read speakers
        speaker_path = os.path.join(dataset.path, SPEAKER_INFO_FILE_NAME)
        for speaker_idx, speaker_info in jsonfile.read_json_file(speaker_path).items():
            speaker = dataset.add_speaker(speaker_idx=speaker_idx)
            speaker.load_speaker_info_from_dict(speaker_info)

        # Read utt2spk
        utt2spk_path = os.path.join(dataset.path, UTT2SPK_FILE_NAME)
        utt2spk = textfile.read_key_value_lines(utt2spk_path, separator=' ')

        # Read utterances
        utterance_path = os.path.join(dataset.path, UTTERANCE_FILE_NAME)
        for utterance_idx, utt_info in textfile.read_separated_lines_with_first_key(utterance_path, separator=' ', max_columns=4).items():
            start = None
            end = None

            if len(utt_info) > 1:
                start = float(utt_info[1])

            if len(utt_info) > 2:
                end = float(utt_info[2])

            speaker_idx = None

            if utterance_idx in utt2spk.keys():
                speaker_idx = utt2spk[utterance_idx]

            dataset.add_utterance(utt_info[0], utterance_idx=utterance_idx, speaker_idx=speaker_idx, start=start, end=end)

        # Read segmentations
        for seg_file in glob.glob(os.path.join(dataset.path, 'segmentation_*.txt')):
            file_name = os.path.basename(seg_file)
            key = file_name[len('segmentation_'):len(file_name) - len('.txt')]

            utterance_segments = collections.defaultdict(list)

            for record in textfile.read_separated_lines_generator(seg_file, separator=' ', max_columns=4):
                utterance_segments[record[0]].append(segmentation.Segment(record[3], float(record[1]), float(record[2])))

            for utterance_idx, segments in utterance_segments.items():
                dataset.add_segmentation(utterance_idx, segments=segments, key=key)

    def save(self, dataset, path):
        os.makedirs(path, exist_ok=True)

        # Write files
        file_path = os.path.join(path, FILES_FILE_NAME)
        file_records = {file.idx: file.path for file in dataset.files.values()}
        textfile.write_separated_lines(file_path, file_records, separator=' ', sort_by_column=0)

        # Write speakers
        speaker_path = os.path.join(path, SPEAKER_INFO_FILE_NAME)
        speaker_data = {speaker.idx: speaker.get_speaker_info_dict() for speaker in dataset.speakers.values()}
        jsonfile.write_json_to_file(speaker_path, speaker_data)

        # Write utterances
        utterance_path = os.path.join(path, UTTERANCE_FILE_NAME)
        utterance_records = {utterance.idx: [utterance.file_idx, utterance.start, utterance.end] for utterance in dataset.utterances.values()}
        textfile.write_separated_lines(utterance_path, utterance_records, separator=' ', sort_by_column=0)

        # Write utt2spk
        utt2spk_path = os.path.join(path, UTT2SPK_FILE_NAME)
        utt2spk_records = {utterance.idx: utterance.speaker_idx for utterance in dataset.utterances.values()}
        textfile.write_separated_lines(utt2spk_path, utt2spk_records, separator=' ', sort_by_column=0)

        # Write segmentations
        segmentations_by_key = collections.defaultdict(dict)

        for utterance_idx, utt_segmentations in dataset.segmentations.items():
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
