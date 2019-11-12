import unittest
import ply.lex as leex

import rdfscript.reader as reader

class ReaderWhitespaceTest(unittest.TestCase):

    def setUp(self):
        self.reader = leex.lex(module=reader)
        self.reader.open_brackets = 0

    def tearDown(self):
        None

    def test_line_numbers(self):
        self.reader.input('\n\n\nSymbol')
        token = self.reader.token()

        self.assertEqual(token.lineno, 4)

    def test_whitespace_not_tokenised(self):
        self.reader.input('\n\n\n\n\t\n')
        token = self.reader.token()

        self.assertEqual(token, None)


if __name__ == '__main__':
    unittest.main()
