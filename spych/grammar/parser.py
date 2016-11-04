from abc import ABCMeta
from abc import abstractmethod


class BaseParser(metaclass=ABCMeta):
    @abstractmethod
    def parse_string(self, data):
        pass

    def parse_from_file(self, file_path):
        f = open(file_path, 'r')
        content = f.read()
        f.close()

        return self.parse_string(content)

    @abstractmethod
    def write_string(self, model):
        pass

    def write_to_file(self, model, file_path):
        f = open(file_path, 'w')
        f.write(self.write_string(model))
        f.close()
