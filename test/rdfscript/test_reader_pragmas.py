import unittest
import ply.lex as leex

import rdfscript.reader as reader

class ReaderPragmaTest(unittest.TestCase):

    def setUp(self):
        self.reader = leex.lex(module=reader)
        self.reader.open_brackets = 0

    def tearDown(self):
        None

    def test_prefix(self):
        self.reader.input('@prefix prefix <http://example/test/>')

        tokens = []

        for token in self.reader:
            tokens.append(token)

        self.assertEqual([x.type for x in tokens], ['PREFIX', 'SYMBOL', 'URI'])


if __name__ == '__main__':
    unittest.main()


