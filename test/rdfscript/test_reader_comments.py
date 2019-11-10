import unittest
import ply.lex as leex

import rdfscript.reader as reader

class ReaderCommentTest(unittest.TestCase):

    def setUp(self):
        self.reader = leex.lex(module=reader)
        self.reader.open_brackets = 0

    def tearDown(self):
        None

    def test_comments_whole_line(self):
        self.reader.input('#Symbol 123 4.56 true')
        token = self.reader.token()

        self.assertEqual(token, None)

    def test_comments_mid_line(self):
        self.reader.input('Symbol #comment at end')
        token = self.reader.token()

        self.assertEqual(token.type, 'SYMBOL')
        token = self.reader.token()
        self.assertEqual(token, None)

if __name__ == '__main__':
    unittest.main()
