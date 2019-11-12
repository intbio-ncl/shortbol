import unittest
import ply.lex as leex

import rdfscript.reader as reader

class ReaderSymbolTest(unittest.TestCase):

    def setUp(self):
        self.reader = leex.lex(module=reader)
        self.reader.at_line_start = True
        self.reader.indent_stack = [0]

    def tearDown(self):
        None

    def test_symbol_alpha(self):
        self.reader.input('Symbol')
        token = self.reader.token()

        self.assertEqual(token.value, 'Symbol')
        self.assertEqual(token.type, 'SYMBOL')

    def test_symbol_alphanumeric(self):
        self.reader.input('Sym801')
        token = self.reader.token()

        self.assertEqual(token.value, 'Sym801')
        self.assertEqual(token.type, 'SYMBOL')

    def test_symbol_start_numeric(self):
        self.reader.input('5ymb0l')
        token = self.reader.token()

        self.assertEqual(token.value, 5)
        self.assertEqual(token.type, 'INTEGER')

    def test_symbol_start_plus(self):
        self.reader.input('+')
        token = self.reader.token()

        self.assertEqual(token.value, '+')
        self.assertEqual(token.type, 'SYMBOL')

    def test_symbol_equals(self):
        self.reader.input('=')
        token = self.reader.token()

        self.assertEqual(token.value, '=')
        self.assertEqual(token.type, '=')

    def test_symbol_forward_slash(self):
        self.reader.input('symbol/end /end end/')

        token = self.reader.token()
        self.assertEqual(token.value, 'symbol/end')
        self.assertEqual(token.type, 'SYMBOL')

        token = self.reader.token()
        self.assertEqual(token.value, '/end')
        self.assertEqual(token.type, 'SYMBOL')

        token = self.reader.token()
        self.assertEqual(token.value, 'end/')
        self.assertEqual(token.type, 'SYMBOL')

    def test_symbol_hash(self):
        self.reader.input('start#end #start end#')

        token = self.reader.token()
        self.assertEqual(token.value, 'start#end')
        self.assertEqual(token.type, 'SYMBOL')

        token = self.reader.token()
        self.assertEqual(token.value, '#start')
        self.assertEqual(token.type, 'SYMBOL')

        token = self.reader.token()
        self.assertEqual(token.value, 'end#')
        self.assertEqual(token.type, 'SYMBOL')

    def test_symbol_colon(self):
        self.reader.input('start:end :end start:')

        token = self.reader.token()
        self.assertEqual(token.value, 'start:end')
        self.assertEqual(token.type, 'SYMBOL')

        token = self.reader.token()
        self.assertEqual(token.value, ':end')
        self.assertEqual(token.type, 'SYMBOL')

        token = self.reader.token()
        self.assertEqual(token.value, 'start:')
        self.assertEqual(token.type, 'SYMBOL')

if __name__ == '__main__':
    unittest.main()
