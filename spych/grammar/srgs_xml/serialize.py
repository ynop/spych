import xml.etree.ElementTree as et

from spych.grammar import model


class SRGSXMLSerializer:
    def create_grammar_element(self, grammar):
        grammar_element = et.Element('grammar')

        for rule in grammar.rules:
            rule_element = self.create_rule_element(rule)
            grammar_element.append(rule_element)

        grammar_element.set('version', '1.0')
        grammar_element.set('xmlns', 'http://www.w3.org/2001/06/grammar')
        if grammar.language is not None:
            grammar_element.set('xml:lang', grammar.language)
        else:
            grammar_element.set('xml:lang', 'en-US')

        if grammar.root_rule is not None:
            grammar_element.set('root', grammar.root_rule.name)
        elif len(grammar.rules) > 0:
            grammar_element.set('root', grammar.rules[0].name)

        return grammar_element

    def create_rule_element(self, rule):
        rule_element = et.Element("rule")
        rule_element.set('id', rule.name)

        if rule.scope == model.Rule.SCOPE_PUBLIC:
            rule_element.set('scope', 'public')

        self.add_model_element_to_xml_element(rule_element, rule.value)

        return rule_element

    def add_model_element_to_xml_element(self, xml_element, model_element):
        the_element = None

        if isinstance(model_element, model.Token):
            the_element = self.add_token_to_xml_element(xml_element, model_element)
        elif isinstance(model_element, model.RuleReference):
            the_element = self.add_rule_reference_to_xml_element(xml_element, model_element)
        elif isinstance(model_element, model.Group):
            the_element = self.add_group_to_xml_element(xml_element, model_element)
        elif isinstance(model_element, model.OptionalGroup):
            the_element = self.add_optional_group_to_xml_element(xml_element, model_element)
        elif isinstance(model_element, model.Sequence):
            the_element = self.add_sequence_to_xml_element(xml_element, model_element)
        elif isinstance(model_element, model.Alternatives):
            the_element = self.add_alternatives_to_xml_element(xml_element, model_element)

        self.set_repetitions_on_xml_element(the_element, model_element)
        self.add_tags_to_element(the_element, model_element)

    def add_token_to_xml_element(self, xml_element, token):
        xml_element.text = token.value

        return xml_element

    def add_rule_reference_to_xml_element(self, xml_element, rule_reference):
        ref_element = et.SubElement(xml_element, 'ruleref')
        ref_element.set('uri', '#' + rule_reference.rule_name)

        return ref_element

    def add_group_to_xml_element(self, xml_element, group):
        group_element = et.SubElement(xml_element, 'item')
        self.add_model_element_to_xml_element(group_element, group.value)

        return group_element

    def add_optional_group_to_xml_element(self, xml_element, optional_group):
        group_element = et.SubElement(xml_element, 'item')
        group_element.set('repeat', '0-1')
        self.add_model_element_to_xml_element(group_element, optional_group.value)

        return group_element

    def add_sequence_to_xml_element(self, xml_element, sequence):
        seq_element = et.SubElement(xml_element, 'item')
        for element in sequence.elements:
            item_element = et.SubElement(seq_element, 'item')
            self.add_model_element_to_xml_element(item_element, element)

        return seq_element

    def add_alternatives_to_xml_element(self, xml_element, alternatives):
        alt_element = et.SubElement(xml_element, 'one-of')
        for element in alternatives.elements:
            item_element = et.SubElement(alt_element, 'item')
            if element.weight != 1:
                item_element.set('weight', str(element.weight))
            self.add_model_element_to_xml_element(item_element, element)

        return alt_element

    def set_repetitions_on_xml_element(self, xml_element, model_element):
        if model_element.min_repeat == 1 and model_element.max_repeat == 1:
            return

        if model_element.max_repeat == model.Element.INFINITY_REPEAT:
            xml_element.set('repeat', '{}-'.format(model_element.min_repeat))
        else:
            xml_element.set('repeat', '{}-{}'.format(model_element.min_repeat, model_element.max_repeat))

    def add_tags_to_element(self, xml_element, model_element):
        for tag in model_element.tags:
            tag_element = et.SubElement(xml_element, 'tag')
            tag_element.text = tag.name
