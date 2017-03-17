import os
import shutil
import tempfile

from spych.data import dataset


def spych_dataset_path():
    return os.path.join(os.path.dirname(__file__), 'spych_ds')


def get_wav_file_path(name):
    return os.path.join(os.path.dirname(__file__), 'wav_files', name)


def create_dataset():
    temp_path = tempfile.mkdtemp()
    
    ds = dataset.Dataset(temp_path)

    wav_1_path = get_wav_file_path('wav_1.wav')
    wav_2_path = get_wav_file_path('wav_2.wav')
    wav_3_path = get_wav_file_path('wav_3.wav')
    wav_4_path = get_wav_file_path('wav_4.wav')

    file_1 = ds.add_file(wav_1_path)
    file_2 = ds.add_file(wav_2_path, file_idx='wav_2')
    file_3 = ds.add_file(wav_3_path, file_idx='wav_3')
    file_4 = ds.add_file(wav_4_path, file_idx='wav_4')

    speaker_1 = ds.add_speaker()
    speaker_2 = ds.add_speaker(speaker_idx='spk-2')
    speaker_3 = ds.add_speaker(speaker_idx='spk-3')

    utt_1 = ds.add_utterance(file_1.idx, speaker_idx=speaker_1.idx)
    utt_2 = ds.add_utterance(file_2.idx, utterance_idx='utt-2', speaker_idx=speaker_1.idx)
    utt_3 = ds.add_utterance(file_3.idx, utterance_idx='utt-3', speaker_idx=speaker_2.idx, start=0, end=15)
    utt_4 = ds.add_utterance(file_3.idx, utterance_idx='utt-4', speaker_idx=speaker_2.idx, start=15, end=25)
    utt_5 = ds.add_utterance(file_4.idx, speaker_idx=speaker_3.idx)

    segm_1 = ds.add_segmentation(utt_1.idx, segments='who am i')
    segm_2 = ds.add_segmentation(utt_2.idx, segments='who are you')
    segm_3 = ds.add_segmentation(utt_3.idx, segments='who is he')
    segm_4 = ds.add_segmentation(utt_4.idx, segments='who are they')
    segm_5 = ds.add_segmentation(utt_5.idx, segments='who is she')

    sv = dataset.Subview(filtered_utterances=['utt-2', 'utt-4'])
    ds.add_subview('sv', sv)

    return ds


def create_invalid_dataset():
    temp_path = tempfile.mkdtemp()

    ds = dataset.Dataset(temp_path)

    wav_1_path = get_wav_file_path('wav_1.wav')
    wav_2_path = get_wav_file_path('wav_2.wav')
    wav_3_path = get_wav_file_path('empty.wav')
    wav_4_path = get_wav_file_path('wav_invalid.wav')

    file_1 = ds.add_file(wav_1_path)
    file_2 = ds.add_file(wav_2_path, file_idx='wav_2')
    file_3 = ds.add_file(wav_3_path, file_idx='wav_3')
    file_4 = ds.add_file(wav_4_path, file_idx='wav_4')

    speaker_1 = ds.add_speaker(gender='f')
    speaker_2 = ds.add_speaker(speaker_idx='spk-2', gender='m')
    speaker_3 = ds.add_speaker(speaker_idx='spk-3')

    utt_1 = ds.add_utterance(file_1.idx, speaker_idx=speaker_1.idx)
    utt_2 = ds.add_utterance(file_2.idx, utterance_idx='utt-2', speaker_idx=speaker_1.idx)
    utt_3 = ds.add_utterance(file_3.idx, utterance_idx='utt-3', speaker_idx=speaker_2.idx, start=0, end=15)
    utt_4 = ds.add_utterance(file_3.idx, utterance_idx='utt-4', speaker_idx=speaker_2.idx, start=15, end=25)

    segm_1 = ds.add_segmentation(utt_1.idx, segments='who am i')
    segm_3 = ds.add_segmentation(utt_3.idx, segments='who is he')
    segm_4 = ds.add_segmentation(utt_4.idx, segments='who are they')

    file_2.path = '/hey/this/is/somethingnotexitstingyeihhibideidei'

    utt_4.file_idx = None
    utt_3.start = 17
    utt_3.end = 8

    utt_2.speaker_idx = None

    return ds