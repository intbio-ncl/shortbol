import unittest

from rdfscript.parser import Parser

from rdfscript.core import Name, Value, Identifier
from rdfscript.template import Property, Expansion


class ParserExpansionTest(unittest.TestCase):

    def setUp(self):
        self.parser = Parser()
        self.maxDiff = None

    def tearDown(self):
        None

    def test_expansion_no_args_no_body(self):
        forms = self.parser.parse('e is a a()')
        expect = Expansion(Identifier(Name('e')),
                           Identifier(Name('a')),
                           [],
                           [])
        self.assertEqual(expect, forms[0])

    def test_expansion_one_arg_no_body(self):
        forms = self.parser.parse('e is a a(12345)')
        expect = Expansion(Identifier(Name('e')),
                           Identifier(Name('a')),
                           [Value(12345)],
                           [])
        self.assertEqual(expect, forms[0])

    def test_expansion_multi_args_no_body(self):
        forms = self.parser.parse('e is a a(12345, 54321)')
        expect = Expansion(Identifier(Name('e')),
                           Identifier(Name('a')),
                           [Value(12345),
                            Value(54321)],
                           [])

        self.assertEqual(expect, forms[0])

    def test_expansion_expansion_as_arg(self):
        forms = self.parser.parse('e is a a(f is a b(12345))')
        f = self.parser.parse('f is a b(12345)')[0]
        expect = Expansion(Identifier(Name('e')),
                           Identifier(Name('a')),
                           [f],
                           [])
        self.assertEqual(expect, forms[0])

    def test_expansion_no_args_with_body(self):
        forms = self.parser.parse('e is a a()(x=true)')
        expect = Expansion(Identifier(Name('e')),
                           Identifier(Name('a')),
                           [],
                           [Property(Identifier(Name('x')), Value(True))])
        self.assertEqual(expect, forms[0])

    def test_expansion_one_arg_with_body(self):
        forms = self.parser.parse('e is a a(12345)(x=true)')
        expect = Expansion(Identifier(Name('e')),
                           Identifier(Name('a')),
                           [Value(12345)],
                           [Property(Identifier(Name('x')), Value(True))])
        self.assertEqual(expect, forms[0])

    def test_expansion_multi_args_with_body(self):
        forms = self.parser.parse('e is a a(12345, 54321)(x=true)')
        expect = Expansion(Identifier(Name('e')),
                           Identifier(Name('a')),
                           [Value(12345),
                            Value(54321)],
                           [Property(Identifier(Name('x')), Value(True))])

        self.assertEqual(expect, forms[0])

    def test_expansion_multiple_properties(self):
        forms = self.parser.parse('e is a a()(x=true y=false)')
        expect = Expansion(Identifier(Name('e')),
                           Identifier(Name('a')),
                           [],
                           [Property(Identifier(Name('x')), Value(True)),
                            Property(Identifier(Name('y')), Value(False))])
        self.assertEqual(expect, forms[0])
