def index_name_if_in_list(name, name_list, suffix=''):
    """
    Adds an index to the given name if it already exists in the given list.

    :param name: Name
    :param name_list: List of names that the new name must differ from.
    :param suffix: The suffix to append after the index.
    :return: Unique name
    """
    new_name = '{}{}'.format(name, suffix)
    index = 1

    while new_name in name_list:
        new_name = '{}_{}{}'.format(name, index, suffix)
        index+= 1

    return new_name
