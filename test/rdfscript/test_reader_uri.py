import unittest
import ply.lex as leex

import rdfscript.reader as reader

class ReaderURITest(unittest.TestCase):

    def setUp(self):
        self.reader = leex.lex(module=reader)
        self.reader.at_line_start = True
        self.reader.indent_stack = [0]

    def tearDown(self):
        None

    def test_uri(self):
        self.reader.input('<http://uri.org/example#fragment>')
        token = self.reader.token()

        self.assertEqual(token.value, 'http://uri.org/example#fragment')
        self.assertEqual(token.type, 'URI')

    def test_multiple_uris(self):
        self.reader.input('<http://uri.org/example#fragment> <http://uri.org/example#2>')
        first_token = self.reader.token()
        second_token = self.reader.token()

        self.assertEqual(first_token.value, 'http://uri.org/example#fragment')
        self.assertEqual(first_token.type, 'URI')

        self.assertEqual(second_token.value, 'http://uri.org/example#2')
        self.assertEqual(second_token.type, 'URI')

if __name__ == '__main__':
    unittest.main()
