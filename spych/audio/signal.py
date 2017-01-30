import os

import numpy as np
import scipy.io.wavfile

from spych.assets import audacity


def calculate_energy_of_samples(samples):
    """
    Calculate the energy of a signal.

    :param samples: The samples of the signal.
    :return: Energy
    """
    values = np.abs(samples).astype(np.int)

    if type(values) == list:
        values = np.array(values)

    return np.sum(np.power(values, 2)) / values.size


def add_noise_to_signal(signal, noise, snr=None):
    """
    Adds the noise to the given signal with the desired SNR.

    :param signal: signal samples
    :param noise: noise samples
    :param snr: signal-to-noise ratio [dB], if not given the signal and noise are mixed equally
    :return: The resulting samples
    """
    added_noise = np.copy(noise)

    if snr is not None:
        signal_energy = calculate_energy_of_samples(signal)
        noise_energy = calculate_energy_of_samples(noise)

        current_ratio = signal_energy / noise_energy
        target_ratio = np.power(10, (snr / 10.0))

        noise_scaler = np.sqrt(current_ratio / target_ratio)
        added_noise = added_noise * noise_scaler

    return (signal * 0.5 + added_noise * 0.5).astype(signal.dtype)


def add_random_noise_to_signal(signal, snr=0):
    """
    Add generated noise to the given signal with the desired SNR.

    :param signal: signal samples
    :param snr: signal-to-noise ratio [dB]
    :return: The resulting samples
    """
    noise = np.random.normal(0, 1, signal.size)
    max_amp = np.iinfo(signal.dtype).max
    noise = (noise / np.max(np.abs(noise))) * max_amp
    noise = noise.astype(signal.dtype)

    return add_noise_to_signal(signal, noise, snr=snr)


def add_noise_to_wav(signal_path, noise_path, output_path, snr=None):
    """
    Creates a wav with the signal and the given noise added with the desired SNR.

    If noise is smaller than signal, it is repeated.
    If noise is bigger than signal, noise is randomly truncated.

    :param signal_path: Path to signal wav
    :param noise_path: Path to noise wav
    :param output_path: Path to store the resulting signal
    :param snr: signal-to-noise ratio [dB]
    """
    signal_sampling_rate, signal_samples = scipy.io.wavfile.read(signal_path)
    noise_sampling_rate, noise_samples = scipy.io.wavfile.read(noise_path)

    if signal_sampling_rate != noise_sampling_rate:
        raise ValueError("Signal and noise have different sampling rates. ({} - {})".format(signal_sampling_rate, noise_sampling_rate))

    if noise_samples.size > signal_samples.size:
        max_start_index = noise_samples.size - signal_samples.size
        start_index = np.random.randint(max_start_index + 1)
        noise_samples = noise_samples[start_index:start_index + signal_samples.size]

    if noise_samples.size < signal_samples.size:
        noise_parts = []
        noise_sample_count = 0

        while noise_sample_count < signal_samples.size:
            max_to_add = signal_samples.size - noise_sample_count
            noise_parts.append(noise_samples.copy()[:max_to_add])
            noise_sample_count += noise_samples.size

        noise_samples = np.concatenate(noise_parts)

    output_samples = add_noise_to_signal(signal_samples, noise_samples, snr=snr)
    scipy.io.wavfile.write(output_path, signal_sampling_rate, output_samples)


def add_random_noise_to_wav(wav_path, output_path, snr=None):
    """
    Creates a wav file with the given signal and generated noise added with the desired SNR.

    :param wav_path: Path to the signal wav
    :param output_path: Path to store the resulting wav.
    :param snr: signal-to-noise ratio [dB]
    """
    sampling_rate, samples = scipy.io.wavfile.read(wav_path)
    new_samples = add_random_noise_to_signal(samples, snr=snr)
    scipy.io.wavfile.write(output_path, sampling_rate, new_samples)


def get_sample_index_from_seconds(seconds, sampling_rate):
    """
    Get sample index with time in seconds.

    :param seconds: Time to convert to sample index.
    :param sampling_rate: Sampling rate
    :return: Sample index
    """
    return int(seconds * sampling_rate)


def calculate_snr(signal, noise):
    """
    Calculate SNR between signal and noise samples.

    :param signal: Signal
    :param noise: Noise
    :return: Signal-To-Noise Ratio [dB]
    """
    signal_energy = calculate_energy_of_samples(signal)
    noise_energy = calculate_energy_of_samples(noise)

    return 10 * np.log10(signal_energy / noise_energy)


def estimate_snr_with_labels(signal, sampling_rate, labels):
    """
    Estimate SNR of signal with labels. If label is one of ('speech', 'signal') it is considered as signal otherwise as noise.

    :param signal: Samples
    :param sampling_rate: Sampling rate
    :param labels: Labels (start [sec], end [sec], label)
    :return:
    """
    signal_labels = []

    for label in labels:
        signal_labels.append([
            get_sample_index_from_seconds(label[0], sampling_rate),
            get_sample_index_from_seconds(label[1], sampling_rate),
            label[2]
        ])

    noise_sample_chunks = []
    signal_sample_chunks = []

    sample_index = 0
    label_index = 0

    while sample_index < signal.size:

        if label_index < len(signal_labels):
            next_label = signal_labels[label_index]

            if sample_index == next_label[0]:
                chunk = signal[next_label[0]:next_label[1] + 1]
                if next_label[2] in ['speech', 'signal']:
                    signal_sample_chunks.append(chunk)
                else:
                    noise_sample_chunks.append(chunk)

                sample_index = next_label[1] + 1
                label_index += 1
            else:
                noise_sample_chunks.append(signal[sample_index:next_label[0]])
                sample_index = next_label[0]
        else:
            noise_sample_chunks.append(signal[sample_index:signal.size])
            sample_index = signal.size

    noise_samples = np.concatenate(noise_sample_chunks)
    signal_samples = np.concatenate(signal_sample_chunks)

    return calculate_snr(signal_samples, noise_samples)


def clip_segments(signal, sampling_rate, segments={}):
    """
    Extract the given segments from signal.

    e.g. segments:

    {
        # label : (start, end)
        'ax' : (1.5, 7.4),
        'by' : (19.4, 24.5)
    }

    :param signal: Samples ndarray
    :param segments: Dictionary with segments
    :return: Dictionary with (label/samples)
    """

    output = {}

    for label, range in segments.items():
        start = range[0]
        end = range[1]

        start_sample = round(start * sampling_rate)
        end_sample = round(end * sampling_rate)

        output[label] = signal[start_sample:end_sample]

    return output


def clip_segments_from_wav(wav_path, audacity_label_path, output_directory):
    """

    :param wav_path:
    :param segments:
    :param output_directory:
    :return:
    """

    sampling_rate, samples = scipy.io.wavfile.read(wav_path)
    labels = audacity.read_label_file(audacity_label_path)

    segments = {}

    for label in labels:
        name = label[2]
        index = 1

        while name in segments.keys():
            name = '{}_{}'.format(label[2], index)
            index += 1

        segments[name] = (label[0], label[1])

    parts = clip_segments(samples, sampling_rate, segments)

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for label, samples in parts.items():
        path = os.path.join(output_directory, '{}.wav'.format(label))
        scipy.io.wavfile.write(path, sampling_rate, samples)
