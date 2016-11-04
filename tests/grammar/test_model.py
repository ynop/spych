from pyspeechgrammar import model

__author__ = 'buec'

import unittest


class GrammarTestCase(unittest.TestCase):
    def setUp(self):
        self.gram = model.Grammar()
        self.rule_a = model.Rule(name="id")
        self.gram.add_rule(self.rule_a)

    def test_add_rule_should_succeed(self):
        rule_b = model.Rule(name="b")

        self.assertEqual(1, len(self.gram.rules))

        self.gram.add_rule(rule_b)

        self.assertEqual(2, len(self.gram.rules))

    def test_add_rule_with_existing_name_should_raise_value_error(self):
        rule_b = model.Rule(name="id")

        with self.assertRaises(ValueError):
            self.gram.add_rule(rule_b)

    def test_contains_rule_with_name_should_return_false(self):
        self.assertFalse(self.gram.contains_rule_with_name("x"))

    def test_remove_rule_should_succeed(self):
        self.assertEqual(1, len(self.gram.rules))
        self.gram.remove_rule(self.rule_a)
        self.assertEqual(0, len(self.gram.rules))


if __name__ == '__main__':
    unittest.main()
