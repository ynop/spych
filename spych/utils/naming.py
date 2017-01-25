def index_name_if_in_list(name, name_list, suffix='', prefix=''):
    """
    Adds an index to the given name if it already exists in the given list.

    :param name: Name
    :param name_list: List of names that the new name must differ from.
    :param suffix: The suffix to append after the index.
    :param prefix: The prefix to append in front of the index.
    :return: Unique name
    """
    new_name = '{}{}{}'.format(prefix, name, suffix)
    index = 1

    while new_name in name_list:
        new_name = '{}_{}{}{}'.format(name, prefix, index, suffix)
        index+= 1

    return new_name
