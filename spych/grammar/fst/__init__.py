from spych.grammar import parser
from spych.grammar.fst import serialize


class FSTParser(parser.BaseParser):
    def parse_string(self, data):
        pass

    def write_string(self, data):
        serializer = serialize.FSTSerializer(data)
        return serializer.serialize()[0]

    def write_to_file(self, model, file_path):
        serializer = serialize.FSTSerializer(model)
        fst, labels = serializer.serialize()

        f = open(file_path, 'w')
        f.write(fst)
        f.close()

        label_path = file_path + ".labels"

        f = open(label_path, 'w')
        f.write(labels)
        f.close()
