import random
import string


def index_name_if_in_list(name, name_list, suffix='', prefix=''):
    """
    Adds an index to the given name if it already exists in the given list.

    :param name: Name
    :param name_list: List of names that the new name must differ from.
    :param suffix: The suffix to append after the index.
    :param prefix: The prefix to append in front of the index.
    :return: Unique name
    """
    new_name = '{}'.format(name)
    index = 1

    while new_name in name_list:
        new_name = '{}_{}{}{}'.format(name, prefix, index, suffix)
        index+= 1

    return new_name


def generate_name(length=15, not_in=None):
    """
    Generates a random string of lowercase letters with the given length.

    :param length: Length of the string to output.
    :param not_in: Only return a string not in the given iterator.
    :return:
    """
    value = ''.join(random.choice(string.ascii_lowercase) for i in range(length))

    while (not_in is not None) and (value in not_in):
        value = ''.join(random.choice(string.ascii_lowercase) for i in range(length))

    return value