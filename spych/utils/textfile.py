import os

from spych.utils import text


def read_separated_lines(path, separator=' ', max_columns=-1):
    """
    Reads a text file where each line represents a record with some separated columns.

    :param path: Path to the file to read.
    :param separator: Separator that is used to split the columns.
    :param max_columns: Number of max columns (if the separator occurs within the last column).
    :return: list
    """

    gen = read_separated_lines_generator(path, separator, max_columns)
    return list(gen)


def read_separated_lines_with_first_key(path, separator=' ', max_columns=-1):
    """
    Reads the separated lines of a file and returns a dictionary with the first column as keys, value is a list with the rest of the columns.

    :param path: Path to the file to read.
    :param separator: Separator that is used to split the columns.
    :param max_columns: Number of max columns (if the separator occurs within the last column).
    :return: dict
    """
    gen = read_separated_lines_generator(path, separator, max_columns)

    dic = {}

    for record in gen:
        if len(record) > 0:
            dic[record[0]] = record[1:len(record)]

    return dic


def read_key_value_lines(path, separator=' ', default_value=''):
    """
    Reads lines of a text file with two columns as key/value dictionary.

    :param path: Path to the file.
    :param separator: Separator that is used to split key and value.
    :param default_value: If no value is given this value is used.
    :return: dict
    """
    gen = read_separated_lines_generator(path, separator, 2)

    dic = {}

    for record in gen:
        if len(record) > 1:
            dic[record[0]] = record[1]
        elif len(record) > 0:
            dic[record[0]] = default_value

    return dic


def write_separated_lines(path, values, separator=' ', sort_by_column=0):
    """
    Writes list or dict to file line by line. Dict can have list as value then they written separated on the line.

    :param path: Path to write file to.
    :param values: Dict or list
    :param separator: Separator to use between columns.
    :param sort_by_column: if >= 0, sorts the list by the given index, if its 0 or 1 and its a dictionary it sorts it by either the
    key (0) or value (1). By default 0, meaning sorted by the first column or the key.
    :return:
    """
    f = open(path, 'w', encoding='utf-8')

    if type(values) is dict:
        if sort_by_column in [0, 1]:
            items = sorted(values.items(), key=lambda t: t[sort_by_column])
        else:
            items = values.items()

        for key, value in items:
            if type(value) is list:
                value = separator.join(value)

            f.write('{}{}{}\n'.format(key, separator, value))
    elif type(values) is list:
        if 0 <= sort_by_column < len(values):
            items = sorted(values)
        else:
            items = values

        for record in items:
            str_values = [str(value) for value in record]

            f.write('{}\n'.format(separator.join(str_values)))

    f.close()


def read_separated_lines_generator(path, separator=' ', max_columns=-1, ignore_lines_starting_with=[]):
    """
    Creates a generator through all lines of a file and returns the splitted line.

    :param path: Path to the file.
    :param separator: Separator that is used to split the columns.
    :param max_columns: Number of max columns (if the separator occurs within the last column).
    :param ignore_lines_starting_with: Lines starting with a string in this list will be ignored.
    :return: generator
    """
    if not os.path.isfile(path):
        print('File doesnt exist or is no file: {}'.format(path))
        return

    f = open(path, 'r', errors='ignore', encoding='utf-8')

    if max_columns > -1:
        max_splits = max_columns - 1
    else:
        max_splits = -1

    for line in f:
        stripped_line = line.strip()
        should_ignore = text.starts_with_prefix_in_list(stripped_line, ignore_lines_starting_with)

        if not should_ignore and stripped_line != '':
            record = stripped_line.split(sep=separator, maxsplit=max_splits)
            record = [field.strip() for field in record]
            yield record

    f.close()
