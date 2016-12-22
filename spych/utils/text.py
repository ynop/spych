import re


def remove_punctuation(text, exceptions=[]):
    """
    Removes the punctuation from a string.

    :param text: Text
    :return: Text without punctuation.
    """

    all_but = [
        '\w',
        '\s'
    ]

    all_but.extend(exceptions)

    pattern = '[^{}]'.format(''.join(all_but))

    return re.sub(pattern, '', text)


def starts_with_prefix_in_list(text, prefixes):
    """
    Checks if the given string starts with one of the prefixes in the list.

    :param text: Text
    :param prefixes: List of prefixes
    :return: True/False
    """
    for prefix in prefixes:
        if text.startswith(prefix):
            return True
    return False
