import re


def remove_punctuation(text):
    """
    Removes the punctuation from a string.

    :param text: Text
    :return: Text without punctuation.
    """
    return re.sub(r'[^\w\s]', '', text)


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
