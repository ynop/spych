__author__ = 'buec'

import xml.etree.ElementTree as et
import xml.dom.minidom

from pyspeechgrammar import parser
from pyspeechgrammar import model

from pyspeechgrammar.srgs_xml import serialize

class SRGSXMLParser(parser.BaseParser):

    def __init__(self):
        self.serializer = serialize.SRGSXMLSerializer()

    def parse_string(self, data):
        pass


    def write_string(self, data):
        grammar_element = self.serializer.create_grammar_element(data)

        xml_value = xml.dom.minidom.parseString(et.tostring(grammar_element))
        return xml_value.toprettyxml(indent="  ")
