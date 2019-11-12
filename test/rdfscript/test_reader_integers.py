import unittest
import ply.lex as leex

import rdfscript.reader as reader

class ReaderIntegerTest(unittest.TestCase):

    def setUp(self):
        self.reader = leex.lex(module=reader)
        self.reader.at_line_start = True
        self.reader.indent_stack = [0]

    def tearDown(self):
        None

    def test_integer(self):
        self.reader.input('12345')
        token = self.reader.token()

        self.assertEqual(token.value, 12345)
        self.assertEqual(token.type, 'INTEGER')

    def test_integer(self):
        self.reader.input('-12345')
        token = self.reader.token()

        self.assertEqual(token.value, -12345)
        self.assertEqual(token.type, 'INTEGER')

    def test_integer_alpha(self):
        self.reader.input('12E45')
        token = self.reader.token()

        self.assertEqual(token.value, 12)
        self.assertEqual(token.type, 'INTEGER')

if __name__ == '__main__':
    unittest.main()
