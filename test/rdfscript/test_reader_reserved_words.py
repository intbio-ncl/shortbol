import unittest
import ply.lex as leex

import rdfscript.reader as reader

class ReaderReservedTest(unittest.TestCase):

    def setUp(self):
        self.reader = leex.lex(module=reader)
        self.reader.at_line_start = True
        self.reader.indent_stack = [0]

    def tearDown(self):
        None

    def test_is_a(self):
        self.reader.input('is a')

        token = self.reader.token()
        self.assertEqual(token.type, 'ISA')
        self.assertEqual(token.value, 'is a')

    def test_is_a_double_identifier(self):
        self.reader.input('this ape')

        token = self.reader.token()
        self.assertEqual(token.type, 'SYMBOL')
        self.assertEqual(token.value, 'this')

        token = self.reader.token()
        self.assertEqual(token.type, 'SYMBOL')
        self.assertEqual(token.value, 'ape')

    def test_is_a_more_whitespace(self):
        self.reader.input('is   a')

        token = self.reader.token()
        self.assertEqual(token.type, 'ISA')
        self.assertEqual(token.value, 'is a')

    def test_from(self):
        self.reader.input('from')

        token = self.reader.token()
        self.assertEqual(token.type, 'FROM')

    def test_from_inside_symbol(self):
        self.reader.input('fromage fromfrom')

        token = self.reader.token()
        self.assertEqual(token.type, 'SYMBOL')
        self.assertEqual(token.value, 'fromage')

        token = self.reader.token()
        self.assertEqual(token.type, 'SYMBOL')
        self.assertEqual(token.value, 'fromfrom')
