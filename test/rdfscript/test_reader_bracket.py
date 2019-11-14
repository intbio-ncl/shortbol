import unittest
import ply.lex as leex

import rdfscript.reader as reader

class ReaderBracketTrackingTest(unittest.TestCase):

    def setUp(self):
        self.reader = leex.lex(module=reader)
        self.reader.open_brackets = 0

    def tearDown(self):
        None

    def test_balanced_brackets_no_brackets(self):
        self.reader.input('12345 67890')
        token = self.reader.token()
        self.assertEqual(0, self.reader.open_brackets)

        token = self.reader.token()
        self.assertEqual(0, self.reader.open_brackets)

    def test_balanced_brackets_one_pair_brackets(self):
        self.reader.input('(12345) 67890')
        token = self.reader.token()
        self.assertEqual(1, self.reader.open_brackets)

        token = self.reader.token()
        self.assertEqual(1, self.reader.open_brackets)

        token = self.reader.token()
        self.assertEqual(0, self.reader.open_brackets)

        token = self.reader.token()
        self.assertEqual(0, self.reader.open_brackets)

    def test_balanced_brackets_nested_brackets(self):
        self.reader.input('(12345)(()())((()))')
        for token in self.reader:
            pass
        
        token = self.reader.token()
        self.assertEqual(0, self.reader.open_brackets)


