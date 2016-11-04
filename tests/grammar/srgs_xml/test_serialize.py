__author__ = 'buec'

import xml.etree.ElementTree as et

import unittest

from pyspeechgrammar.srgs_xml import serialize
from pyspeechgrammar import model


class SRGSXMLParser(unittest.TestCase):

    def setUp(self):
        self.serializer = serialize.SRGSXMLSerializer()

    def test_create_grammar_element(self):
        token1 = model.Token(value='token content 1')
        rule1 = model.Rule(name='rule name 1', value=token1)
        token2 = model.Token(value='token content 2')
        rule2 = model.Rule(name='rule name 2', value=token2)
        grammar = model.Grammar(name='grammar', language='en-US')
        grammar.root_rule = rule1
        grammar.add_rule(rule1)
        grammar.add_rule(rule2)

        grammar_element = self.serializer.create_grammar_element(grammar)

        self.assertEqual(2, len(grammar_element))
        self.assertEqual('http://www.w3.org/2001/06/grammar', grammar_element.get('xmlns'))
        self.assertEqual('1.0', grammar_element.get('version'))
        self.assertEqual('en-US', grammar_element.get('xml:lang'))
        self.assertEqual('rule name 1', grammar_element.get('root'))

    def test_create_rule_element(self):
        token = model.Token(value='token content')
        rule = model.Rule(name='rule name')
        rule.value = token
        rule_element = self.serializer.create_rule_element(rule)

        self.assertEqual('rule', rule_element.tag)
        self.assertEqual('rule name', rule_element.get('id'))
        self.assertEqual('token content', rule_element.text)
        self.assertIsNone(rule_element.get('scope'))

    def test_create_rule_element_public(self):
        token = model.Token(value='token content')
        rule = model.Rule(name='rule name')
        rule.value = token
        rule.scope = model.Rule.SCOPE_PUBLIC
        rule_element = self.serializer.create_rule_element(rule)

        self.assertEqual('rule', rule_element.tag)
        self.assertEqual('rule name', rule_element.get('id'))
        self.assertEqual('token content', rule_element.text)
        self.assertEqual('public', rule_element.get('scope'))

    def test_add_model_element_to_xml_element_adds_tags(self):
        root = et.Element('root')
        token = model.Token(value='token content')
        token.add_tag(model.Tag('tag1'))
        token.add_tag(model.Tag('tag2'))

        self.serializer.add_model_element_to_xml_element(root, token)
        self.assertEqual(2, len(root))

    def test_add_model_element_to_xml_element_sets_repeat(self):
        root = et.Element('root')
        token = model.Token(value='token content', min_repeat=2, max_repeat=4)

        self.serializer.add_model_element_to_xml_element(root, token)
        self.assertEqual('2-4', root.get('repeat'))

    def test_add_token_to_xml_element(self):
        root = et.Element('root')
        token = model.Token(value='token content')

        self.serializer.add_token_to_xml_element(root, token)
        self.assertEqual('token content', root.text)

    def test_add_rule_reference_to_xml_element(self):
        root = et.Element('root')
        ref = model.RuleReference(rule_name='rule')

        self.serializer.add_rule_reference_to_xml_element(root, ref)
        self.assertEqual(1, len(root))
        self.assertEqual('#rule', root[0].get('uri'))

    def test_add_group_to_xml_element(self):
        root = et.Element('root')
        token = model.Token(value='token content')
        group = model.Group(value=token)

        self.serializer.add_group_to_xml_element(root, group)
        self.assertEqual(1, len(root))
        self.assertEqual('token content', root[0].text)

    def test_add_optional_group_to_xml_element(self):
        root = et.Element('root')
        token = model.Token(value='token content')
        group = model.OptionalGroup(value=token)

        self.serializer.add_optional_group_to_xml_element(root, group)
        self.assertEqual(1, len(root))
        self.assertEqual('0-1', root[0].get('repeat'))
        self.assertEqual('token content', root[0].text)

    def test_add_sequence_to_xml_element(self):
        root = et.Element('root')
        token1 = model.Token(value='token content 1')
        token2 = model.Token(value='token content 2')
        sequence = model.Sequence()
        sequence.add_element(token1)
        sequence.add_element(token2)

        self.serializer.add_sequence_to_xml_element(root, sequence)
        self.assertEqual(1, len(root))
        self.assertEqual(2, len(root[0]))
        self.assertEqual('token content 1', root[0][0].text)
        self.assertEqual('token content 2', root[0][1].text)

    def test_add_alternatives_to_xml_element(self):
        root = et.Element('root')
        token1 = model.Token(value='token content 1')
        token2 = model.Token(value='token content 2')
        alt = model.Alternatives()
        alt.add_element(token1)
        alt.add_element(token2)

        self.serializer.add_alternatives_to_xml_element(root, alt)
        self.assertEqual(1, len(root))
        self.assertEqual(2, len(root[0]))
        self.assertEqual('one-of', root[0].tag)
        self.assertEqual('token content 1', root[0][0].text)
        self.assertEqual('token content 2', root[0][1].text)

    def test_set_repetitions_on_xml_element(self):
        root = et.Element('root')
        model_element = model.Token(value='token content', min_repeat=2, max_repeat=4)

        self.serializer.set_repetitions_on_xml_element(root, model_element)
        self.assertEqual('2-4', root.get('repeat'))

    def test_set_repetitions_on_xml_element_default(self):
        root = et.Element('root')
        model_element = model.Token(value='token content', min_repeat=1, max_repeat=1)

        self.serializer.set_repetitions_on_xml_element(root, model_element)
        self.assertEqual(None, root.get('repeat'))

    def test_set_repetitions_on_xml_element_infinity(self):
        root = et.Element('root')
        model_element = model.Token(value='token content', min_repeat=3, max_repeat=model.Element.INFINITY_REPEAT)

        self.serializer.set_repetitions_on_xml_element(root, model_element)
        self.assertEqual('3-', root.get('repeat'))

    def test_add_tags_to_xml_element(self):
        root = et.Element('root')
        model_element = model.Token(value='token content')
        model_element.add_tag(model.Tag('tag1'))
        model_element.add_tag(model.Tag('tag2'))

        self.serializer.add_tags_to_element(root, model_element)
        self.assertEqual(2, len(root))
        self.assertEqual('tag1', root[0].text)
        self.assertEqual('tag2', root[1].text)

