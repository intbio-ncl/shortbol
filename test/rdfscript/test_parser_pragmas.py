import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex

from rdfscript.parser import Parser

from rdfscript.pragma import (PrefixPragma,
                              DefaultPrefixPragma,
                              ExtensionPragma,
                              ImportPragma)

from rdfscript.core import Uri, Name, Identifier


class ParserPragmaTest(unittest.TestCase):

    def setUp(self):
        self.parser = Parser()

    def tearDown(self):
        None

    def test_prefix_pragma_uri(self):
        script = "@prefix Prefix = <http://example.eg/>"
        expected = [PrefixPragma('Prefix',
                                 Identifier(Uri('http://example.eg/')))]
        actually = self.parser.parse(script)
        self.assertEqual(expected, actually)

    def test_prefix_pragma_name(self):
        script = "@prefix Prefix = name"
        expected = [PrefixPragma('Prefix', Identifier(Name('name')))]
        actually = self.parser.parse(script)
        self.assertEqual(expected, actually)

    def test_default_prefix_pragma(self):
        script = "@prefix Prefix"
        expected = [DefaultPrefixPragma('Prefix')]
        actually = self.parser.parse(script)
        self.assertEqual(expected, actually)

    def test_import_pragma_uri(self):
        script = "@use <import>"
        expected = [ImportPragma(Identifier(Uri('import')))]
        actually = self.parser.parse(script)
        self.assertEqual(expected, actually)

        script = "use <import>"
        expected = [ImportPragma(Identifier(Uri('import')))]
        actually = self.parser.parse(script)
        self.assertEqual(expected, actually)

    def test_import_pragma_name(self):
        script = "@use this.target"
        expected = [ImportPragma(Identifier(Name('this'), Name('target')))]
        actually = self.parser.parse(script)
        self.assertEqual(expected, actually)

        script = "use this.target"
        actually = self.parser.parse(script)
        self.assertEqual(expected, actually)

    def test_extension_pragma(self):
        expected = [ExtensionPragma('E', [])]
        actually = self.parser.parse('@extension E()')
        self.assertEqual(expected, actually)


if __name__ == '__main__':
    unittest.main()
