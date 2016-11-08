import requests
import bs4
import urllib.request
import os
import shutil
import tarfile

from spych.data import dataset
from spych.utils import textfile


class VoxforgeConverter(object):
    """
    Downloads files from voxforge page and creates spych dataset from it.

    example url: http://www.repository.voxforge1.org/downloads/de/Trunk/Audio/Main/16kHz_16bit/

    """
    def __init__(self, target_folder, url):
        self.target_folder = target_folder
        self.url = url

        self.download_folder = os.path.join(self.target_folder, '__download')
        self.extraction_folder = os.path.join(self.target_folder, '__extracted')

        self.dataset = None
        self.number_of_downloaded_files = 0

    def get_dataset(self):
        self.dataset = dataset.Dataset(dataset_folder=self.target_folder)
        self.dataset.save()

        self.prepare_folders()
        self.number_of_downloaded_files = self.download_data()
        self.import_downloaded_files()
        self.dataset.save()
        self.cleanup()

        return self.dataset

    def prepare_folders(self):
        os.makedirs(self.download_folder, exist_ok=True)
        os.makedirs(self.extraction_folder, exist_ok=True)

    def cleanup(self):
        #shutil.rmtree(self.download_folder, ignore_errors=True)
        shutil.rmtree(self.extraction_folder, ignore_errors=True)

    def download_data(self):
        """
        Downloads all .tgz files linked from the given url into the target folder.
        """
        page = requests.get(self.url)
        soup = bs4.BeautifulSoup(page.text, "html.parser")
        links = [a.attrs.get('href') for a in soup.select('a[href]')]

        to_download = []

        for link in links:
            if str(link).endswith('.tgz'):
                to_download.append(link)

        number_of_files = len(to_download)
        print('Found {} files to download.'.format(number_of_files))

        for index, link in enumerate(to_download):
            full_url = self.url + '/' + link
            full_path = os.path.join(self.download_folder, link)

            if not os.path.exists(full_path):
                print("{}/{} Download {}".format(index + 1, number_of_files, link))
                urllib.request.urlretrieve(full_url, filename=full_path)

        return number_of_files

    def import_downloaded_files(self):
        index = 0
        for file in os.listdir(self.download_folder):
            if file.endswith('.tgz'):
                index += 1
                print("{}/{} Import data from file {}".format(index, self.number_of_downloaded_files, file))

                self.add_data_from_tar_to_dataset(file)

    def add_data_from_tar_to_dataset(self, filename):
        tar = tarfile.open(os.path.join(self.download_folder, filename), "r")
        tar.extractall(self.extraction_folder)
        tar.close()

        basename, __ = os.path.splitext(filename)
        extracted_data = os.path.join(self.extraction_folder, basename)

        etc_folder = os.path.join(extracted_data, 'etc')
        audio_folder = os.path.join(extracted_data, 'wav')

        # get info
        info = self.load_readme(etc_folder)
        prompts_file = os.path.join(etc_folder, 'PROMPTS')
        prompts = textfile.read_key_value_lines(prompts_file)
        prompts_raw_file = os.path.join(etc_folder, 'prompts-original')
        prompts_raw = textfile.read_key_value_lines(prompts_raw_file)

        speaker, gender = self.get_speaker_and_gender(extracted_data, info)

        if str(info['File type']).lower() == 'flac':
            print('ignore because of filetype: flac')
            return False

        if int(info['Number of channels']) > 1:
            print('ignore because of channels > 1')
            return False

        # get data
        wavs = {}
        segments = {}
        transcriptions = {}
        transcriptions_raw = {}
        utt2spk = {}
        speakers = {speaker: gender}

        for key, value in prompts.items():
            wav_id = os.path.basename(key)
            utterance_id = '{}_{}'.format(speaker, wav_id)
            audio_file_name = '{}.{}'.format(wav_id, info['File type'].lower())
            audio_file_path = os.path.join(audio_folder, audio_file_name)

            if os.path.exists(audio_file_path):
                wavs[wav_id] = audio_file_path
                segments[utterance_id] = [wav_id]
                transcriptions[utterance_id] = value
                transcriptions_raw[wav_id] = prompts_raw[wav_id]
                utt2spk[utterance_id] = speaker

        wav_id_mapping = self.dataset.import_wavs(wavs, copy_files=True)
        utt_id_mapping = self.dataset.add_utterances(segments, wav_id_mapping=wav_id_mapping)
        speaker_id_mapping = self.dataset.set_utt2spk(speakers)
        self.dataset.set_transcriptions(transcriptions, utt_id_mapping=utt_id_mapping)
        self.dataset.set_transcriptions_raw(transcriptions_raw, utt_id_mapping=utt_id_mapping)
        self.dataset.set_utt2spk(utt2spk, utt_id_mapping=utt_id_mapping, speaker_id_mapping=speaker_id_mapping)

    def get_speaker_and_gender(self, path, info):
        speaker = None
        gender = None

        if not 'User Name' in info.keys() or info['User Name'] == 'Name:anonymous':
            speaker = os.path.basename(path).replace('-', '')
        else:
            speaker = info['User Name']

        if info['Gender'] in ['Männlich', 'Male', 'Mnnlich']:
            gender = 'm'
        elif info['Gender'] in ['Weiblich', 'Female']:
            gender = 'f'

        return speaker, gender

    def load_readme(self, etc_folder):
        readme_file = os.path.join(etc_folder, 'README')
        info = {}

        f = open(readme_file, 'r', errors='ignore')

        for raw_line in f:
            line = raw_line.strip()
            if line is not None and line is not '':
                line = line.rstrip(';.')
                parts = line.split(':', maxsplit=1)

                if len(parts) > 1:
                    info[parts[0].strip()] = parts[1].strip()
                elif len(parts) > 0:
                    info[parts[0].strip()] = ''

        f.close()

        return info
