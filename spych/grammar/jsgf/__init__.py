import re

from spych.grammar import parser
from spych.grammar.jsgf import grammars


class JSGFParser(parser.BaseParser):
    def parse_string(self, data):
        p = grammars.Grammar.parser()

        # remove newlines after alternative separator (performance issue)
        jsgf_string = self._remove_newlines_within_alternatives(data)

        # add whitespace before groups, rulerefs (easier and faster in parsing)
        jsgf_string = self._add_space_around_rule_expansions(jsgf_string)

        parsed_jsgf_data = p.parse_string(jsgf_string)

        return parsed_jsgf_data.model

    def _remove_newlines_within_alternatives(self, jsgf_string):
        regex = re.compile(r"\s*\|\s*")
        return regex.sub(" | ", jsgf_string)

    def _add_space_around_rule_expansions(self, jsgf_string):
        result = str(jsgf_string).replace("(", " (")
        result = str(result).replace(")", ") ")
        result = str(result).replace("[", " [")
        result = str(result).replace("]", "] ")
        result = str(result).replace("<", " <")
        result = str(result).replace(">", "> ")

        return result

    def write_string(self, model):
        pass
