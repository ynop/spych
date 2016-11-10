import json


def write_json_to_file(path, data):
    """
    Writes data as json to file.

    :param path: Path to write to
    :param data: Data
    """
    f = open(path, 'w')
    json.dump(data, f)
    f.close()


def read_json_file(path):
    """
    Reads json file.

    :param path: Path to read
    :return: Data
    """
    f = open(path, 'r')
    data = json.load(f)
    f.close()

    return data
