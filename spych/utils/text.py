
def remove_punctuation(text):
    """
    Removes the punctuation from a string.

    :param text: Text
    :return: Text without punctuation.
    """
    return str(text).replace(r'\w+', '')
