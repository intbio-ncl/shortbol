import unittest

from rdfscript.rdfscriptparser import RDFScriptParser

from rdfscript.core import Name, Value, Uri
from rdfscript.template import (Property,
                                Expansion)

class ParserExpansionTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()
        self.maxDiff = None

    def tearDown(self):
        None

    def test_expansion_no_args_no_body(self):

        forms = self.parser.parse('e is a a()')
        expect = Expansion(Name('e'),
                           Name('a'),
                           [],
                           [])

        self.assertEqual(expect, forms[0])

    def test_expansion_one_arg_no_body(self):

        forms = self.parser.parse('e is a a(12345)')
        expect = Expansion(Name('e'),
                           Name('a'),
                           [Value(12345)],
                           [])

        self.assertEqual(expect, forms[0])

    def test_expansion_multi_args_no_body(self):

        forms = self.parser.parse('e is a a(12345, 54321)')
        expect = Expansion(Name('e'),
                           Name('a'),
                           [Value(12345),
                            Value(54321)],
                           [])

        self.assertEqual(expect, forms[0])

    def test_expansion_expansion_as_arg(self):

        forms = self.parser.parse('e is a a(f is a b(12345))')
        f = self.parser.parse('f is a b(12345)')[0]
        expect = Expansion(Name('e'),
                           Name('a'),
                           [f],
                           [])

        self.assertEqual(expect, forms[0])


    def test_expansion_no_args_with_body(self):

        forms = self.parser.parse('e is a a()(x=true)')
        expect = Expansion(Name('e'),
                           Name('a'),
                           [],
                           [Property(Name('x'), Value(True))])

        self.assertEqual(expect, forms[0])

    def test_expansion_one_arg_with_body(self):

        forms = self.parser.parse('e is a a(12345)(x=true)')
        expect = Expansion(Name('e'),
                           Name('a'),
                           [Value(12345)],
                           [Property(Name('x'), Value(True))])

        self.assertEqual(expect, forms[0])

    def test_expansion_multi_args_with_body(self):

        forms = self.parser.parse('e is a a(12345, 54321)(x=true)')
        expect = Expansion(Name('e'),
                           Name('a'),
                           [Value(12345),
                            Value(54321)],
                           [Property(Name('x'), Value(True))])

        self.assertEqual(expect, forms[0])

    def test_expansion_multiple_properties(self):

        forms = self.parser.parse('e is a a()(x=true y=false)')
        expect = Expansion(Name('e'),
                           Name('a'),
                           [],
                           [Property(Name('x'), Value(True)),
                            Property(Name('y'), Value(False))])

        self.assertEqual(expect, forms[0])
