import unittest
import ply.lex as leex

import rdfscript.reader as reader

class ReaderSpecialsTest(unittest.TestCase):

    def setUp(self):
        self.reader = leex.lex(module=reader)
        self.reader.open_brackets = 0

    def tearDown(self):
        None

    def test_boolean_reserved(self):
        self.reader.input('true false')
        first_token = self.reader.token()
        second_token = self.reader.token()

        self.assertEqual(first_token.value, 'true')
        self.assertEqual(first_token.type, 'BOOLEAN')

        self.assertEqual(second_token.value, 'false')
        self.assertEqual(second_token.type, 'BOOLEAN')

    def test_literal_lparen(self):
        self.reader.input('(')
        token = self.reader.token()

        self.assertEqual(token.value, '(')
        self.assertEqual(token.type, '(')

    def test_literal_rparen(self):
        self.reader.input(')')
        token = self.reader.token()

        self.assertEqual(token.value, ')')
        self.assertEqual(token.type, ')')

    def test_literal_comma(self):
        self.reader.input(',')
        token = self.reader.token()

        self.assertEqual(token.value, ',')
        self.assertEqual(token.type, ',')

    def test_literal_dot(self):
        self.reader.input('.')
        token = self.reader.token()

        self.assertEqual(token.value, '.')
        self.assertEqual(token.type, '.')

    def test_literal_rbracket(self):
        self.reader.input(']')
        token = self.reader.token()

        self.assertEqual(token.value, ']')
        self.assertEqual(token.type, ']')

    def test_literal_lbracket(self):
        self.reader.input('[')
        token = self.reader.token()

        self.assertEqual(token.value, '[')
        self.assertEqual(token.type, '[')

if __name__ == '__main__':
    unittest.main()
