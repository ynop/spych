import modgrammar
import sys

from spych.grammar import model


class JavaIdentifier(modgrammar.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (modgrammar.WORD("A-Za-z$", "A-Za-z0-9_$"))

    def grammar_elem_init(self, session_data):
        self.value = self[0].string


class Package(modgrammar.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (modgrammar.LIST_OF(JavaIdentifier, sep=".", min=1))

    def grammar_elem_init(self, session_data):
        self.value = self[0].string


class SelfIdentifyingHeader(modgrammar.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (modgrammar.LITERAL("#JSGF"), modgrammar.WHITESPACE,
               modgrammar.WORD("A-Za-z0-9._\-"),
               modgrammar.OPTIONAL(modgrammar.WHITESPACE, modgrammar.WORD("A-Za-z0-9._\-")),
               modgrammar.OPTIONAL(modgrammar.WHITESPACE, modgrammar.WORD("A-Za-z0-9._\-")),
               modgrammar.LITERAL(";"), modgrammar.LITERAL('\n'))

    def grammar_elem_init(self, session_data):
        self.version = self[2].string

        if self[3] is not None:
            self.encoding = self[3][1].string
        else:
            self.encoding = None

        if self[4] is not None:
            self.locale = self[4][1].string
        else:
            self.locale = None


class NameDeclaration(modgrammar.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (modgrammar.LITERAL("grammar"), modgrammar.WHITESPACE,
               modgrammar.OPTIONAL(Package, modgrammar.LITERAL('.')),
               JavaIdentifier,
               modgrammar.LITERAL(";"))

    def grammar_elem_init(self, session_data):
        self.name = self[3].value

        if self[2] is None:
            self.package = None
        else:
            self.package = self[2][0].value


class ImportStatement(modgrammar.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (
        modgrammar.LITERAL("import"), modgrammar.WHITESPACE, modgrammar.LITERAL("<"),
        Package,
        modgrammar.LITERAL('.'),
        JavaIdentifier | modgrammar.LITERAL('*'),
        modgrammar.LITERAL(">"),
        modgrammar.LITERAL(";"), modgrammar.OPTIONAL(modgrammar.WHITESPACE))

    def grammar_elem_init(self, session_data):
        self.package = self[3].value
        self.rule = self[5].string


class Header(modgrammar.Grammar):
    grammar_whitespace_mode = 'optional'
    grammar = (SelfIdentifyingHeader, NameDeclaration, modgrammar.ZERO_OR_MORE(ImportStatement))

    def grammar_elem_init(self, session_data):
        self.version = self[0].version
        self.encoding = self[0].encoding
        self.locale = self[0].locale
        self.name = self[1].name
        self.package = self[1].package
        self.imports = []

        for i in range(len(self[2].elements)):
            self.imports.append(self[2][i])


class PublicModifier(modgrammar.Grammar):
    grammar_whitespace_mode = 'optional'
    grammar = (modgrammar.LITERAL("public"))


class MetaCharacter(modgrammar.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (modgrammar.OR(modgrammar.L(';'), modgrammar.L('='), modgrammar.L('|'), modgrammar.L('*'),
                             modgrammar.L('+'), modgrammar.L('<'), modgrammar.L('>'), modgrammar.L('('),
                             modgrammar.L(')'), modgrammar.L('['), modgrammar.L(']'), modgrammar.L('{'),
                             modgrammar.L('}'), modgrammar.L('/*'), modgrammar.L('*/'), modgrammar.L('//'),
                             modgrammar.L(" "), modgrammar.L('"')))


class Tag(modgrammar.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (modgrammar.L('{'), modgrammar.ZERO_OR_MORE(modgrammar.ANY_EXCEPT('^}')), modgrammar.L('}'))

    def grammar_elem_init(self, session_data):
        self.model = model.Tag(name=self[1].string)


class UnaryOperator(modgrammar.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (modgrammar.OPTIONAL(modgrammar.WHITESPACE),
               modgrammar.L('*') |
               modgrammar.L('+') |
               modgrammar.LIST_OF(Tag, sep=" ", min=1))

    def grammar_elem_init(self, session_data):
        self.is_kleene_star = False
        self.is_plus = False
        self.tags = []

        if self[1].string == '*':
            self.is_kleene_star = True
        elif self[1].string == '+':
            self.is_plus = True
        else:
            for i in range(0, len(self[1].elements), 2):
                self.tags.append(self[1][i].model)


class Token(modgrammar.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (modgrammar.ONE_OR_MORE(modgrammar.EXCEPT(modgrammar.ANY(""), MetaCharacter)))

    def grammar_elem_init(self, session_data):
        self.model = model.Token(value=self[0].string.strip())


class QuotedToken(modgrammar.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (modgrammar.LITERAL('"'), modgrammar.OPTIONAL(Token), modgrammar.ONE_OR_MORE(modgrammar.WHITESPACE, Token),
               modgrammar.LITERAL('"'))

    def grammar_elem_init(self, session_data):
        if self[1] is not None:
            value = self[1].string + self[2].string
        else:
            value = self[2].string

        self.model = model.Token(value=value.strip())


class RuleReference(modgrammar.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (modgrammar.L('<'),
               modgrammar.OPTIONAL(Package, modgrammar.L('.')),
               JavaIdentifier,
               modgrammar.L('>'))

    def grammar_elem_init(self, session_data):
        if self[1] is not None:
            value = self[1].string + self[2].string
        else:
            value = self[2].string

        self.model = model.RuleReference(value)


class Group(modgrammar.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (modgrammar.L('('), modgrammar.OPTIONAL(modgrammar.WHITESPACE),
               modgrammar.REF("RuleExpansion", module=sys.modules[__name__]),
               modgrammar.OPTIONAL(modgrammar.WHITESPACE), modgrammar.L(')'))

    def grammar_elem_init(self, session_data):
        self.model = model.Group(self[2].model)


class OptionalGroup(modgrammar.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (modgrammar.L('['), modgrammar.OPTIONAL(modgrammar.WHITESPACE),
               modgrammar.REF("RuleExpansion", module=sys.modules[__name__]),
               modgrammar.OPTIONAL(modgrammar.WHITESPACE), modgrammar.L(']'))

    def grammar_elem_init(self, session_data):
        self.model = model.OptionalGroup(self[2].model)


class SequenceRuleExpansion(modgrammar.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (Token |
               QuotedToken |
               RuleReference |
               Group |
               OptionalGroup,
               modgrammar.OPTIONAL(UnaryOperator))

    def grammar_elem_init(self, session_data):
        self.model = self[0].model

        if self[1] is not None:
            min_repeat = 1
            max_repeat = 1

            if self[1].is_kleene_star:
                min_repeat = 0
                max_repeat = model.Element.INFINITY_REPEAT
            elif self[1].is_plus:
                min_repeat = 1
                max_repeat = model.Element.INFINITY_REPEAT

            self.model.set_repeat(min_repeat, max_repeat)

            for tag in self[1].tags:
                self.model.add_tag(tag)


class Sequence(modgrammar.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (SequenceRuleExpansion,
               modgrammar.WHITESPACE,
               modgrammar.LIST_OF(SequenceRuleExpansion, sep=modgrammar.WHITESPACE, min=1))

    def grammar_elem_init(self, session_data):
        self.model = model.Sequence()
        self.model.add_element(self[0].model)

        for i in range(0, len(self[2].elements), 2):
            self.model.add_element(self[2][i].model)


class AlternativeWeight(modgrammar.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (modgrammar.L("/"), modgrammar.WORD("0-9.", "0-9.ef"), modgrammar.LITERAL("/"), modgrammar.WHITESPACE)

    def grammar_elem_init(self, session_data):
        self.value = self[1].string


class AlternativeSeparator(modgrammar.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (modgrammar.OPTIONAL(modgrammar.WHITESPACE),
               modgrammar.LITERAL("|"),
               modgrammar.OPTIONAL(modgrammar.WHITESPACE))


class AlternativeRuleExpansion(modgrammar.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (Token |
               QuotedToken |
               RuleReference |
               Sequence |
               Group |
               OptionalGroup,
               modgrammar.OPTIONAL(UnaryOperator))

    def grammar_elem_init(self, session_data):
        self.model = self[0].model

        if self[1] is not None:
            min_repeat = 1
            max_repeat = 1

            if self[1].is_kleene_star:
                min_repeat = 0
                max_repeat = model.Element.INFINITY_REPEAT
            elif self[1].is_plus:
                min_repeat = 1
                max_repeat = model.Element.INFINITY_REPEAT

            self.model.set_repeat(min_repeat, max_repeat)

            for tag in self[1].tags:
                self.model.add_tag(tag)


class Alternatives(modgrammar.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (modgrammar.OPTIONAL(AlternativeWeight),
               AlternativeRuleExpansion,
               modgrammar.ONE_OR_MORE(AlternativeSeparator,
                                      modgrammar.OPTIONAL(AlternativeWeight),
                                      AlternativeRuleExpansion
                                      ))

    def grammar_elem_init(self, session_data):
        self.model = model.Alternatives()

        element = self[1].model

        if self[0] is not None:
            element.weight = self[0].value

        self.model.add_element(element)

        for i in range(0, len(self[2].elements)):
            element = self[2][i][2].model

            if self[2][i][1] is not None:
                element.weight = self[2][i][1].value

            self.model.add_element(element)


class RuleExpansion(modgrammar.Grammar):
    grammar_whitespace_mode = 'explicit'
    grammar = (Token | QuotedToken | RuleReference | Sequence | Alternatives | Group | OptionalGroup,
               modgrammar.OPTIONAL(UnaryOperator))

    def grammar_elem_init(self, session_data):
        self.model = self[0].model

        if self[1] is not None:
            min_repeat = 1
            max_repeat = 1

            if self[1].is_kleene_star:
                min_repeat = 0
                max_repeat = model.Element.INFINITY_REPEAT
            elif self[1].is_plus:
                min_repeat = 1
                max_repeat = model.Element.INFINITY_REPEAT

            self.model.set_repeat(min_repeat, max_repeat)

            for tag in self[1].tags:
                self.model.add_tag(tag)


class Rule(modgrammar.Grammar):
    grammar_whitespace_mode = 'optional'
    grammar = (modgrammar.OPTIONAL(PublicModifier),
               modgrammar.LITERAL("<"),
               JavaIdentifier,
               modgrammar.LITERAL(">"),
               modgrammar.LITERAL("="),
               RuleExpansion,
               modgrammar.LITERAL(";"))

    def grammar_elem_init(self, session_data):
        scope = model.Rule.SCOPE_PRIVATE

        if self[0] is not None:
            scope = model.Rule.SCOPE_PUBLIC

        self.model = model.Rule(name=self[2].value, value=self[5].model, scope=scope)


class Grammar(modgrammar.Grammar):
    grammar_whitespace_mode = 'optional'
    grammar = (Header, modgrammar.ZERO_OR_MORE(Rule), modgrammar.OPTIONAL(modgrammar.WHITESPACE), modgrammar.EOI)

    def grammar_elem_init(self, session_data):
        self.model = model.Grammar(name=self[0].name, language=self[0].locale, encoding=self[0].encoding)

        for i in range(len(self[1].elements)):
            rule = self[1][i].model
            self.model.add_rule(rule)

            if rule.scope == model.Rule.SCOPE_PUBLIC and self.model.root_rule is None:
                self.model.root_rule = rule
