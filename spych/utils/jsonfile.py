import json


def write_json_to_file(path, data):
    """
    Writes data as json to file.

    :param path: Path to write to
    :param data: Data
    """
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f)


def read_json_file(path):
    """
    Reads json file.

    :param path: Path to read
    :return: Data
    """

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data
