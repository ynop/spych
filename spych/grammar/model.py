class Grammar:
    def __init__(self, name="", language="en-US", encoding=""):
        self.name = name
        self.language = language
        self.encoding = encoding
        self.rules = []
        self.root_rule = None

    def add_rule(self, rule):
        if self.contains_rule_with_name(rule.name):
            raise ValueError("Grammar already contains a rule with the name '{}'".format(rule.name))

        self.rules.append(rule)

    def remove_rule(self, rule):
        self.rules.remove(rule)

    def contains_rule_with_name(self, rule_name):
        for rule in self.rules:
            if rule.name == rule_name:
                return True

        return False

    def get_rule_with_name(self, rule_name):
        for rule in self.rules:
            if rule.name == rule_name:
                return rule


class Element:
    INFINITY_REPEAT = -1

    def __init__(self, min_repeat=1, max_repeat=1, weight=1):
        self.min_repeat = 1
        self.max_repeat = 1
        self.tags = []
        self.weight = weight

        self.set_repeat(min_repeat, max_repeat)

    def set_repeat(self, min_repeat, max_repeat):
        if min_repeat < 0:
            raise ValueError("Minimal repeat value ({}) has to be greater than or equal 0.".format(min_repeat))

        if max_repeat < Element.INFINITY_REPEAT:
            raise ValueError("Maximal repeat value ({}) has to be greater than or equal 0.".format(max_repeat))

        if min_repeat > max_repeat and max_repeat != Element.INFINITY_REPEAT:
            raise ValueError(
                "Minimal repeat value ({}) has to be greater than or equal to the maximal repeat value ({})".format(min_repeat, max_repeat))

        self.min_repeat = min_repeat
        self.max_repeat = max_repeat

    def add_tag(self, tag):
        self.tags.append(tag)

    def remove_tag(self, tag):
        self.tags.remove(tag)


class ElementContainer:
    def __init__(self):
        self.elements = []

    def add_element(self, element):
        self.elements.append(element)

    def remove_element(self, element):
        self.elements.remove(element)

    def __getitem__(self, index):
        return self.elements[index]


class Rule(Element):
    SCOPE_PRIVATE = 'private'
    SCOPE_PUBLIC = 'public'

    def __init__(self, name="", value=None, scope=SCOPE_PRIVATE, min_repeat=1, max_repeat=1, weight=1):
        super(Rule, self).__init__(min_repeat=min_repeat, max_repeat=max_repeat, weight=weight)
        self.name = name
        self.value = value
        self.scope = scope


class RuleReference(Element):
    def __init__(self, rule_name, min_repeat=1, max_repeat=1, weight=1):
        super(RuleReference, self).__init__(min_repeat=min_repeat, max_repeat=max_repeat, weight=weight)
        self.rule_name = rule_name


class Tag:
    def __init__(self, name):
        super(Tag, self).__init__()
        self.name = name


class Token(Element):
    def __init__(self, value="", min_repeat=1, max_repeat=1, weight=1):
        super(Token, self).__init__(min_repeat=min_repeat, max_repeat=max_repeat, weight=weight)
        self.value = value


class Group(Element):
    def __init__(self, value, min_repeat=1, max_repeat=1, weight=1):
        super(Group, self).__init__(min_repeat=min_repeat, max_repeat=max_repeat, weight=weight)
        self.value = value


class OptionalGroup(Element):
    def __init__(self, value, min_repeat=1, max_repeat=1, weight=1):
        super(OptionalGroup, self).__init__(min_repeat=min_repeat, max_repeat=max_repeat, weight=weight)
        self.value = value


class Sequence(Element, ElementContainer):
    def __init__(self, min_repeat=1, max_repeat=1, weight=1):
        Element.__init__(self, min_repeat=min_repeat, max_repeat=max_repeat, weight=weight)
        ElementContainer.__init__(self)
        pass


class Alternatives(Element, ElementContainer):
    def __init__(self, min_repeat=1, max_repeat=1, weight=1):
        Element.__init__(self, min_repeat=min_repeat, max_repeat=max_repeat, weight=weight)
        ElementContainer.__init__(self)
        pass
