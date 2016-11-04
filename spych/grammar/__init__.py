from spych.grammar import jsgf
from spych.grammar import srgs_xml
from spych.grammar import fst


def convert_jsgf_string_to_srgs_xml_string(jsgf_string):
    p = jsgf.JSGFParser()
    m = p.parse_string(jsgf_string)

    s = srgs_xml.SRGSXMLParser()
    return s.write_string(m)


def convert_jsgf_to_srgs_xml(jsgf_input_file, srgs_output_file):
    p = jsgf.JSGFParser()
    m = p.parse_from_file(jsgf_input_file)

    s = srgs_xml.SRGSXMLParser()
    return s.write_to_file(m, srgs_output_file)


def convert_jsgf_to_fst(jsgf_input_file, fst_output_file):
    p = jsgf.JSGFParser()
    m = p.parse_from_file(jsgf_input_file)

    f = fst.FSTParser()
    return f.write_to_file(m, fst_output_file)
