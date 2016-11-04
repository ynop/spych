__author__ = 'buec'

import unittest
import modgrammar

from pyspeechgrammar.jsgf import grammars
from pyspeechgrammar import model


class JavaIdentifierTest(unittest.TestCase):
    def test_valid_name(self):
        p = grammars.JavaIdentifier.parser()
        result = p.parse_string('AGrammarName0_$')

        self.assertEqual('AGrammarName0_$', result.value)

    def test_invalid_start_character(self):
        p = grammars.JavaIdentifier.parser()

        with self.assertRaises(modgrammar.ParseError):
            result = p.parse_string('_theName')

    def test_invalid_character(self):
        p = grammars.JavaIdentifier.parser()

        with self.assertRaises(modgrammar.ParseError):
            result = p.parse_string('theName(hoi)')


class PackageTest(unittest.TestCase):
    def test_valid_package(self):
        p = grammars.Package.parser()
        result = p.parse_string('all.be.cee')

        self.assertEqual('all.be.cee', result.value)

    def test_valid_single_package(self):
        p = grammars.Package.parser()
        result = p.parse_string('all')

        self.assertEqual('all', result.value)

    def test_invalid_point(self):
        p = grammars.Package.parser()

        with self.assertRaises(modgrammar.ParseError):
            result = p.parse_string('all.')


class SelfIdentifyingHeaderTest(unittest.TestCase):
    def test_version_only(self):
        p = grammars.SelfIdentifyingHeader.parser()
        result = p.parse_string('#JSGF V1.0;\n')

        self.assertEqual(result.version, 'V1.0')
        self.assertEqual(result.encoding, None)
        self.assertEqual(result.locale, None)

    def test_version_and_encoding(self):
        p = grammars.SelfIdentifyingHeader.parser()
        result = p.parse_string('#JSGF V1.0 ISO928943-4;\n')

        self.assertEqual(result.version, 'V1.0')
        self.assertEqual(result.encoding, 'ISO928943-4')
        self.assertEqual(result.locale, None)

    def test_version_and_encoding_and_locale(self):
        p = grammars.SelfIdentifyingHeader.parser()
        result = p.parse_string('#JSGF V1.0 ISO928943-4 en_US;\n')

        self.assertEqual(result.version, 'V1.0')
        self.assertEqual(result.encoding, 'ISO928943-4')
        self.assertEqual(result.locale, 'en_US')

    def test_missing_hash(self):
        p = grammars.SelfIdentifyingHeader.parser()

        with self.assertRaises(modgrammar.ParseError):
            result = p.parse_string('JSGF V1.0 ISO928943-4 en_US;\n')

    def test_missing_newline(self):
        p = grammars.SelfIdentifyingHeader.parser()

        with self.assertRaises(modgrammar.ParseError):
            result = p.parse_string('#JSGF V1.0 ISO928943-4 en_US;')


class NameDeclarationTest(unittest.TestCase):
    def test_name_only(self):
        p = grammars.NameDeclaration.parser()
        result = p.parse_string('grammar SomeName;')

        self.assertEqual(result.name, 'SomeName')
        self.assertEqual(result.package, None)

    def test_name_and_package(self):
        p = grammars.NameDeclaration.parser()
        result = p.parse_string('grammar the.package.SomeName;')

        self.assertEqual(result.name, 'SomeName')
        self.assertEqual(result.package, 'the.package')


class ImportStatementTest(unittest.TestCase):
    def test_single_rule(self):
        p = grammars.ImportStatement.parser()
        result = p.parse_string('import <package.rule>;')

        self.assertEqual(result.package, 'package')
        self.assertEqual(result.rule, 'rule')

    def test_all_rules(self):
        p = grammars.ImportStatement.parser()
        result = p.parse_string('import <package.*>;')

        self.assertEqual(result.package, 'package')
        self.assertEqual(result.rule, '*')

    def test_rule_only(self):
        p = grammars.ImportStatement.parser()

        with self.assertRaises(modgrammar.ParseError):
            p.parse_string('import <rule>;')


class HeaderTest(unittest.TestCase):
    def test_without_imports(self):
        value = '#JSGF V1.0 ISO928943-4;\n' \
                'grammar the.package.SomeName;'

        p = grammars.Header.parser()
        result = p.parse_string(value)

        self.assertEqual(result.version, 'V1.0')
        self.assertEqual(result.encoding, 'ISO928943-4')
        self.assertEqual(result.locale, None)
        self.assertEqual(result.package, 'the.package')
        self.assertEqual(result.name, 'SomeName')

    def test_with_imports(self):
        value = '#JSGF V1.0 ISO928943-4;\n' \
                'grammar the.package.SomeName;\n' \
                'import <package.rule>;\n' \
                'import <other.otherRule>;'

        p = grammars.Header.parser()
        result = p.parse_string(value)

        self.assertEqual(result.version, 'V1.0')
        self.assertEqual(result.encoding, 'ISO928943-4')
        self.assertEqual(result.locale, None)
        self.assertEqual(result.package, 'the.package')
        self.assertEqual(result.name, 'SomeName')
        self.assertEqual(2, len(result.imports))

        self.assertEqual("package", result.imports[0].package)
        self.assertEqual("rule", result.imports[0].rule)
        self.assertEqual("other", result.imports[1].package)
        self.assertEqual("otherRule", result.imports[1].rule)

    def test_missing_self_identifying_header(self):
        value = 'grammar the.package.SomeName;\n' \
                'import <other.otherRule>;'

        p = grammars.Header.parser()

        with self.assertRaises(modgrammar.ParseError):
            p.parse_string(value)

    def test_missing_name_declaration(self):
        value = '#JSGF V1.0 ISO928943-4;\n' \
                'import <other.otherRule>;'

        p = grammars.Header.parser()

        with self.assertRaises(modgrammar.ParseError):
            p.parse_string(value)


class TokenTest(unittest.TestCase):
    def test_valid_token(self):
        p = grammars.Token.parser()
        result = p.parse_string('hallo!')

        self.assertEqual('hallo!', result.model.value)

    def test_invalid_token(self):
        p = grammars.Token.parser()

        with self.assertRaises(modgrammar.ParseError):
            p.parse_string('hallo<hoi')


class QuotedTokenTest(unittest.TestCase):
    def test_valid_token(self):
        p = grammars.QuotedToken.parser()
        result = p.parse_string('"hallo du"')

        self.assertEqual('hallo du', result.model.value)

    def test_invalid_token(self):
        p = grammars.QuotedToken.parser()

        with self.assertRaises(modgrammar.ParseError):
            p.parse_string('hoi du')


class RuleReferenceTest(unittest.TestCase):
    def test_valid_reference(self):
        p = grammars.RuleReference.parser()
        result = p.parse_string('<ruleName>')

        self.assertEqual('ruleName', result.model.rule_name)

    def test_invalid_token(self):
        p = grammars.RuleReference.parser()

        with self.assertRaises(modgrammar.ParseError):
            p.parse_string('<fom')


class GroupTest(unittest.TestCase):
    def test_valid(self):
        p = grammars.Group.parser()
        result = p.parse_string('(ruleName hoi)')

        self.assertIsNotNone(result.model)
        self.assertIsNotNone(result.model.value)

    def test_with_whitespace(self):
        p = grammars.Group.parser()
        result = p.parse_string('(\n ruleName hoi  )')

        self.assertIsNotNone(result.model)
        self.assertIsNotNone(result.model.value)

    def test_empty(self):
        p = grammars.Group.parser()

        with self.assertRaises(modgrammar.ParseError):
            p.parse_string('()')


class OptionalGroupTest(unittest.TestCase):
    def test_valid(self):
        p = grammars.OptionalGroup.parser()
        result = p.parse_string('[ruleName hoi]')

        self.assertIsNotNone(result.model)
        self.assertIsNotNone(result.model.value)

    def test_with_whitespace(self):
        p = grammars.OptionalGroup.parser()
        result = p.parse_string('[\n ruleName hoi  ]')

        self.assertIsNotNone(result.model)
        self.assertIsNotNone(result.model.value)

    def test_empty(self):
        p = grammars.OptionalGroup.parser()

        with self.assertRaises(modgrammar.ParseError):
            p.parse_string('[]')


class SequenceTest(unittest.TestCase):
    def test_sequence_with_two_components(self):
        p = grammars.Sequence.parser()
        result = p.parse_string('ruleName hoi')

        self.assertEqual(2, len(result.model.elements))

    def test_sequence_with_five_components(self):
        p = grammars.Sequence.parser()
        result = p.parse_string('ruleName hoi sali du da')

        self.assertEqual(5, len(result.model.elements))

    def test_sequence_with_five_components_with_more_whitespace(self):
        p = grammars.Sequence.parser()
        result = p.parse_string('ruleName hoi   sali du \t da')

        self.assertEqual(5, len(result.model.elements))

    def test_invalid_sequence(self):
        p = grammars.Sequence.parser()

        with self.assertRaises(modgrammar.ParseError):
            p.parse_string('fom')

    def test_group_within_sequence(self):
        p = grammars.Sequence.parser()
        result = p.parse_string('(c | d) a b')

        self.assertEqual(3, len(result.model.elements))
        self.assertIsInstance(result.model.elements[0], model.Group)


class AlternativeWeightTest(unittest.TestCase):
    def test_valid(self):
        p = grammars.AlternativeWeight.parser()
        result = p.parse_string('/10.23/ ')

        self.assertEqual(result.value, '10.23')


class AlternativesTest(unittest.TestCase):
    def test_alternatives_with_two_components(self):
        p = grammars.Alternatives.parser()
        result = p.parse_string('ruleName | hoi')

        self.assertEqual(2, len(result.model.elements))

    def test_alternatives_with_five_components(self):
        p = grammars.Alternatives.parser()
        result = p.parse_string('ruleName |\n hoi | \n sali |\n du | \n da')

        self.assertEqual(5, len(result.model.elements))

    def test_alternatives_with_five_components_no_space(self):
        p = grammars.Alternatives.parser()
        result = p.parse_string('ruleName | hoi|sali | du | \n da')

        self.assertEqual(5, len(result.model.elements))

    def test_invalid_alternatives(self):
        p = grammars.Alternatives.parser()

        with self.assertRaises(modgrammar.ParseError):
            p.parse_string('fom hoi sali')

    def test_alternative_weights(self):
        p = grammars.Alternatives.parser()
        result = p.parse_string('ruleName | /5/ hoi')

        self.assertEqual(2, len(result.model.elements))
        self.assertEqual("5", result.model.elements[1].weight)

    def test_sequence_within_alternatives(self):
        p = grammars.Alternatives.parser()
        result = p.parse_string('c b | d | a b')

        self.assertEqual(3, len(result.model.elements))
        self.assertIsInstance(result.model.elements[0], model.Sequence)
        self.assertIsInstance(result.model.elements[2], model.Sequence)


class TagTest(unittest.TestCase):
    def test_valid(self):
        p = grammars.Tag.parser()
        result = p.parse_string('{hoi }')

        self.assertEqual(result.model.name, 'hoi ')

    def test_empty(self):
        p = grammars.Tag.parser()
        result = p.parse_string('{}')

        self.assertEqual(result.model.name, '')


class UnaryOperatorTest(unittest.TestCase):
    def test_kleene_star(self):
        p = grammars.UnaryOperator.parser()
        result = p.parse_string('*')

        self.assertTrue(result.is_kleene_star)

    def test_plus(self):
        p = grammars.UnaryOperator.parser()
        result = p.parse_string(' +')

        self.assertTrue(result.is_plus)

    def test_single_tag(self):
        p = grammars.UnaryOperator.parser()
        result = p.parse_string('{hoi}')

        self.assertEqual(1, len(result.tags))

    def test_three_tags(self):
        p = grammars.UnaryOperator.parser()
        result = p.parse_string('{hoi} {sali} {du}')

        self.assertEqual(3, len(result.tags))


class RuleExpansionTest(unittest.TestCase):
    def test_valid_token(self):
        p = grammars.RuleExpansion.parser()
        result = p.parse_string('hio')

        self.assertIsNotNone(result.model)
        self.assertEqual(1, result.model.min_repeat)
        self.assertEqual(1, result.model.max_repeat)
        self.assertEqual(0, len(result.model.tags))
        self.assertIsInstance(result.model, model.Token)

    def test_valid_quoted_token(self):
        p = grammars.RuleExpansion.parser()
        result = p.parse_string('"hio asdf"')

        self.assertIsNotNone(result.model)
        self.assertIsInstance(result.model, model.Token)

    def test_valid_rule_reference(self):
        p = grammars.RuleExpansion.parser()
        result = p.parse_string('<hoi>')

        self.assertIsNotNone(result.model)
        self.assertIsInstance(result.model, model.RuleReference)

    def test_valid_sequence(self):
        p = grammars.RuleExpansion.parser()
        result = p.parse_string('a b c c')

        self.assertIsNotNone(result.model)
        self.assertIsInstance(result.model, model.Sequence)

    def test_valid_alternatives(self):
        p = grammars.RuleExpansion.parser()
        result = p.parse_string('a | b | c')

        self.assertIsNotNone(result.model)
        self.assertIsInstance(result.model, model.Alternatives)

    def test_valid_group(self):
        p = grammars.RuleExpansion.parser()
        result = p.parse_string('(hoi si)')

        self.assertIsNotNone(result.model)
        self.assertIsInstance(result.model, model.Group)

    def test_valid_optinoal_group(self):
        p = grammars.RuleExpansion.parser()
        result = p.parse_string('[ a b]')

        self.assertIsNotNone(result.model)
        self.assertIsInstance(result.model, model.OptionalGroup)

    def test_kleene_star(self):
        p = grammars.RuleExpansion.parser()
        result = p.parse_string('asdf *')

        self.assertIsNotNone(result.model)
        self.assertEqual(0, result.model.min_repeat)
        self.assertEqual(model.Element.INFINITY_REPEAT, result.model.max_repeat)

    def test_plus(self):
        p = grammars.RuleExpansion.parser()
        result = p.parse_string('aasdf+')

        self.assertIsNotNone(result.model)
        self.assertEqual(1, result.model.min_repeat)
        self.assertEqual(model.Element.INFINITY_REPEAT, result.model.max_repeat)

    def test_single_tag(self):
        p = grammars.RuleExpansion.parser()
        result = p.parse_string('asdf{hoi}')

        self.assertEqual(1, len(result.model.tags))

    def test_three_tags(self):
        p = grammars.RuleExpansion.parser()
        result = p.parse_string('asdf {hoi} {sali} {du}')

        self.assertEqual(3, len(result.model.tags))


class RuleTest(unittest.TestCase):
    def test_private(self):
        p = grammars.Rule.parser()
        result = p.parse_string('<rulename> = hoi;')

        self.assertEqual('rulename', result.model.name)
        self.assertEqual(model.Rule.SCOPE_PRIVATE, result.model.scope)
        self.assertIsNotNone(result.model.value)

    def test_public(self):
        p = grammars.Rule.parser()
        result = p.parse_string('public <rulename> = hoi;')

        self.assertEqual('rulename', result.model.name)
        self.assertEqual(model.Rule.SCOPE_PUBLIC, result.model.scope)
        self.assertIsNotNone(result.model.value)

    def test_empty_rule(self):
        p = grammars.Rule.parser()

        with self.assertRaises(modgrammar.ParseError):
            p.parse_string('<rulename> =;')


class GrammarTest(unittest.TestCase):
    def test_one_rule(self):
        value = '#JSGF V1.0 ISO928943-4;\n' \
                'grammar the.package.SomeName;\n' \
                'import <package.rule>;\n' \
                'import <other.otherRule>;' \
                '\n \n  ' \
                'public <rule2> = sali;'

        p = grammars.Grammar.parser()
        result = p.parse_string(value)

        self.assertIsNotNone(result.model)
        self.assertEqual(1, len(result.model.rules))

    def test_four_rules(self):
        value = '#JSGF V1.0 ISO928943-4;\n' \
                'grammar the.package.SomeName;\n' \
                'import <package.rule>;\n' \
                'import <other.otherRule>;' \
                '\n \n  ' \
                'public <rule> = sali;' \
                '\n public <rule2> = sali;' \
                ' public <rule3> = sali;' \
                '\n \n \n \t public <rule4> = sali;'

        p = grammars.Grammar.parser()
        result = p.parse_string(value)

        self.assertIsNotNone(result.model)
        self.assertEqual(4, len(result.model.rules))

    def test_whitespace_at_the_end(self):
        value = '#JSGF V1.0;\n' \
                'grammar someName;\n' \
                'public <rule> = YES | NO;\n'

        p = grammars.Grammar.parser()
        result = p.parse_string(value)

        self.assertIsNotNone(result.model)
        self.assertEqual(1, len(result.model.rules))


if __name__ == '__main__':
    unittest.main()
