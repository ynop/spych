import os


class File(object):
    __slots__ = ['idx', 'path']

    def __init__(self, idx, path):
        self.idx = idx
        self.path = path

    def set_relative_path(self, path):
        """ Sets relative path, with the current basename. """

        basename = os.path.basename(self.path)
        self.path = os.path.join(path, basename)
