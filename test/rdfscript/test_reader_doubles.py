import unittest
import ply.lex as leex

import rdfscript.reader as reader

class ReaderDoubleTest(unittest.TestCase):

    def setUp(self):
        self.reader = leex.lex(module=reader)
        self.reader.open_brackets = 0

    def tearDown(self):
        None

    def test_double(self):
        self.reader.input('0.12345')
        token = self.reader.token()

        self.assertEqual(token.value, 0.12345)
        self.assertEqual(token.type, 'DOUBLE')

    def test_double_alpha(self):
        self.reader.input('0.12E45')
        token = self.reader.token()

        self.assertEqual(token.value, 0.12)
        self.assertEqual(token.type, 'DOUBLE')

if __name__ == '__main__':
    unittest.main()
