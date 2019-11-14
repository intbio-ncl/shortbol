import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex

from rdfscript.rdfscriptparser import RDFScriptParser

from rdfscript.pragma import (PrefixPragma,
                              DefaultPrefixPragma,
                              ExtensionPragma,
                              ImportPragma)

from rdfscript.core import Uri, Name

class ParserPragmaTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()

    def tearDown(self):
        None

    def test_prefix_pragma_uri(self):
        script = "@prefix Prefix = <http://example.eg/>"
        forms  = self.parser.parse(script)

        self.assertEqual(forms,
                         [PrefixPragma('Prefix', Name(Uri('http://example.eg/')))])

    def test_prefix_pragma_name(self):
        script = "@prefix Prefix = name"
        forms  = self.parser.parse(script)

        self.assertEqual(forms,
                         [PrefixPragma('Prefix', Name('name'))])

    def test_default_prefix_pragma(self):
        script = "@prefix Prefix"
        forms  = self.parser.parse(script)

        self.assertEqual(forms,
                         [DefaultPrefixPragma('Prefix')])

    def test_import_pragma_uri(self):
        script = "@use <import>"
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [ImportPragma(Name(Uri('import')))])

        script = "use <import>"
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [ImportPragma(Name(Uri('import')))])

    def test_import_pragma_name(self):
        script = "@use this.target"
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [ImportPragma(Name('this', 'target'))])

        script = "use this.target"
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [ImportPragma(Name('this', 'target'))])

    def test_extension_pragma(self):
        forms = self.parser.parse('@extension E()')

        self.assertEqual(forms, [ExtensionPragma('E', [])])

if __name__ == '__main__':
    unittest.main()
