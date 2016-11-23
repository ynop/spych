import json


def write_json_to_file(path, data):
    """
    Writes data as json to file.

    :param path: Path to write to
    :param data: Data
    """
    f = open(path, 'w', encoding='utf-8')
    json.dump(data, f)
    f.close()


def read_json_file(path):
    """
    Reads json file.

    :param path: Path to read
    :return: Data
    """
    f = open(path, 'r', encoding='utf-8')
    data = json.load(f)
    f.close()

    return data
